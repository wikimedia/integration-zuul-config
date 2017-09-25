node('ServicePipeline') {
  def dockerRegistry = 'docker-registry.wikimedia.org'
  def dockerCredential = 'docker-registry-uploader'
  def dockerRepository = 'wikimedia'

  def name = dockerRepository + '/' + params.ZUUL_PROJECT.replaceAll(/\//, '-')
  def tag = "build-${env.BUILD_ID}"

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
    sh "blubber deploy/blubber.yaml $variant | docker build -t $name:$tag -f - ."
  }

  def run = {
    docker.image("$name:$tag").run()
  }

  def publish = {
    docker.withRegistry("https://$dockerRegistry", dockerCredential) {
      docker.image("$name:$tag").push(tag)
    }
  }

  stage('Setup') {
    checkout(scm)
  }

  stage('Build test image') {
    build('test')
  }

  stage('Test entry point') {
    run()
  }

  stage('Build production image') {
    build('production')
  }

  stage('Register image') {
    publish()
  }
}
