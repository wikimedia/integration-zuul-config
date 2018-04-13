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

  def buildImage = { variant ->
    def labels = imageLabels.collect { "--label '${it}'" }.join(' ')
    sh "blubber $blubberConfig $variant | docker build --pull --tag $fullName $labels --file - ."
  }

  def runImage = {
    timeout(time: 20, unit: 'MINUTES') {
      sh "exec docker run $fullName"
    }
  }

  def publishImage = {
    sh "sudo /usr/local/bin/docker-pusher $fullName"
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
    ].collect { "--set '${it}'" }.join(' ')

    try {
      sh "helm install ${overrides} -n ${release} --debug --wait --timeout ${timeout} ${config.chart}"
      sh "helm test --cleanup ${release}"
    } finally {
      sh "helm delete --purge ${release}"
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
