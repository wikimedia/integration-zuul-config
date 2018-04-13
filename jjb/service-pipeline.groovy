node('ServicePipelineK8s') {
  def blubberConfig = 'dist/pipeline/blubber.yaml'
  def helmConfig = 'dist/pipeline/helm.yaml'
  def servicePort = 31000 + env.EXECUTOR_NUMBER.toInteger()

  def dockerCredential = 'docker-registry-uploader'
  def dockerRepository = 'wikimedia'

  def name = params.ZUUL_PROJECT.replaceAll(/\//, '-')
  def tag = "build-${env.BUILD_ID}"
  def fullName = "$dockerRegistry/$dockerRepository/$name:$tag"

  def imageLabels = [
    "zuul.commit=${params.ZUUL_COMMIT}",
    "jenkins.job=${env.JOB_NAME}",
    "jenkins.build=${env.BUILD_ID}"
  ]

  Map scm = [
    $class: 'GitSCM',
    userRemoteConfigs: [[
      url: "${params.ZUUL_URL}/${params.ZUUL_PROJECT}",
      refspec: params.ZUUL_REF
    ]],
    branches: [[
      name: params.ZUUL_COMMIT
    ]],
    extensions: [
      [$class: 'WipeWorkspace'],
      [$class: 'CloneOption', shallow: true],
      [$class: 'SubmoduleOption', recursiveSubmodules: true]
    ]
  ]

  // Shell argument quoting ripped off from
  // https://issues.jenkins-ci.org/browse/JENKINS-44231#comment-323802
  //
  def arg = { s -> "'" + s.replace("'", "'\\''") + "'" }

  def buildImage = { variant ->
    def labels = imageLabels.collect { "--label ${arg(it)}" }.join(' ')
    sh "blubber $blubberConfig $variant | docker build --pull --tag ${arg(fullName)} $labels --file - ."
  }

  def runImage = {
    timeout(time: 20, unit: 'MINUTES') {
      sh "exec docker run ${arg(fullName)}"
    }
  }

  def publishImage = {
    sh "sudo /usr/local/bin/docker-pusher ${arg(fullName)}"
  }

  def testDeployment = {
    def config = readYaml(file: helmConfig)

    assert config.chart : "you must define 'chart: <helm chart url>' in ${helmConfig}"

    def release = "${name}-${tag}"
    def timeout = 120
    def overrides = [
      "docker.registry=${dockerRegistry}",
      "docker.pull_policy=IfNotPresent",
      "main_app.image=${dockerRepository}/${name}",
      "main_app.version=${tag}",
      "service.port=${servicePort}",
    ].collect { "--set ${arg(it)}" }.join(' ')

    try {
      sh "helm install ${overrides} -n ${arg(release)} --debug --wait --timeout ${timeout} ${arg(config.chart)}"
      sh "helm test --cleanup ${arg(release)}"
    } finally {
      sh "helm delete --purge ${arg(release)}"
    }
  }

  stage('Checkout patch') {
    checkout(scm)
  }

  stage('Build test image') {
    buildImage('test')
  }

  stage('Run test image') {
    runImage()
  }

  stage('Build production image') {
    buildImage('production')
  }

  if (testProductionImage) {
    stage('Test deployment') {
      testDeployment()
    }
  }

  if (pushProductionImage) {
    stage('Register production image') {
      publish()
    }
  }
}
