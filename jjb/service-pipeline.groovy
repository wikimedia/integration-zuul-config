node(nodeLabel) {
  def blubberConfig = '.pipeline/blubber.yaml'
  def helmConfig = '.pipeline/helm.yaml'
  def servicePort = 31000 + env.EXECUTOR_NUMBER.toInteger()

  def dockerCredential = 'docker-registry-uploader'
  def dockerRepository = 'wikimedia'

  def name = params.ZUUL_PROJECT.replaceAll(/\//, '-')
  def shortName = name.split('-').last()

  def tag = new Date().format("yyyyMMddHHmmss", TimeZone.getTimeZone("UTC"))

  def tagTest = "${tag}-test"
  def tagCandidate = "${tag}-candidate"
  def tagProduction = "${tag}-production"

  def testImage = "$dockerRegistry/$dockerRepository/$name:$tagTest"
  def candidateImage = "$dockerRegistry/$dockerRepository/$name:$tagCandidate"
  def productionImage = "$dockerRegistry/$dockerRepository/$name:$tagProduction"

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

  def buildImage = { variant, imageName ->
    def labels = imageLabels.collect { "--label ${arg(it)}" }.join(' ')
    sh "set -o pipefail; blubber $blubberConfig $variant | docker build --pull --tag ${arg(imageName)} $labels --file - ."
  }

  def runImage = { imageName ->
    timeout(time: 20, unit: 'MINUTES') {
      sh "exec docker run ${arg(imageName)}"
    }
  }

  def publishImage = { imageName ->
    sh "sudo /usr/local/bin/docker-pusher ${arg(imageName)}"
  }

  def tagImage = { sourceImage, targetImage ->
    sh "docker tag ${sourceImage} ${targetImage}"
  }

  def cleanImage = { imageName ->
    sh "docker rmi ${arg(imageName)}"
  }

  def cleanImages = { imageNames ->
    imageNames.each { cleanImage(it) }
  }

  def testDeployment = {
    def config = readYaml(file: helmConfig)

    assert config.chart : "you must define 'chart: <helm chart url>' in ${helmConfig}"

    def release = "${shortName}-${tagCandidate}"
    def timeout = 120
    def overrides = [
      "docker.registry=${dockerRegistry}",
      "main_app.image=${dockerRepository}/${name}",
      "main_app.version=${tagCandidate}",
      "service.port=${servicePort}",
    ].collect { "--set ${arg(it)}" }.join(' ')

    try {
      sh "KUBECONFIG=/etc/kubernetes/ci-staging.config helm --tiller-namespace=ci install --namespace=ci ${overrides} -n ${arg(release)} --debug --wait --timeout ${timeout} ${arg(config.chart)}"
      sh "KUBECONFIG=/etc/kubernetes/ci-staging.config helm --tiller-namespace=ci test --cleanup ${arg(release)}"
    } finally {
      sh "KUBECONFIG=/etc/kubernetes/ci-staging.config helm --tiller-namespace=ci delete --purge ${arg(release)}"
    }
  }

  stage('Checkout patch') {
    checkout(scm)
  }

  stage('Build test image') {
    buildImage('test', testImage)
  }

  stage('Run test image') {
    runImage(testImage)
  }

  // Build a candidate production image to be tested in the CI namespace
  if (testProductionImage || pushProductionImage) {
    stage('Build production image') {
      buildImage('production', candidateImage)
    }
  }

  if (testProductionImage) {
    publishImage(candidateImage)
    stage('Test deployment') {
      testDeployment()
    }
  }

  if (pushProductionImage) {
    // Retag the candidate image as the final production image
    tagImage(candidateImage, productionImage)
    stage('Register production image') {
      publishImage(productionImage)
    }

    // Don't keep images on production machine
    cleanImages([testImage, candidateImage, productionImage])
  }
}
