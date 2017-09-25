node(nodeLabel) {
  def blubberConfig = 'deploy/blubber.yaml'

  def dockerRegistry = 'docker-registry.wikimedia.org'
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

  def build = { variant ->
    def labels = imageLabels.collect { "--label '${it}'" }.join(' ')
    sh "blubber $blubberConfig $variant | docker build -t $fullName $labels -f - ."
  }

  def run = {
    timeout(time: 20, unit: 'MINUTES') {
      sh "docker run $fullName"
    }
  }

  def publish = {
    sh "sudo /usr/local/bin/docker-pusher $fullName"
  }

  stage('Checkout patch') {
    checkout(scm)
  }

  stage('Build test image') {
    build('test')
  }

  stage('Run test image') {
    run()
  }

  if (buildProductionImage) {
    stage('Build production image') {
      build('production')
    }

    stage('Register production image') {
      publish()
    }
  }
}
