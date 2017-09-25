node('ServicePipeline') {
  def dockerRegistry = 'docker-registry.wikimedia.org'
  def dockerCredential = 'docker-registry-uploader'
  def dockerRepository = 'wikimedia'

  def name = dockerRepository + '/' + params.ZUUL_PROJECT.replaceAll(/\//, '-')
  def tag = "build-${env.BUILD_ID}"

  stage('Setup') {
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

    checkout scm
  }

  stage('Build test image') {
    build(name, tag, 'test')
  }

  stage('Test entry point') {
    run(name, tag)
  }

  stage('Build production image') {
    build(name, tag, 'production')
  }

  stage('Register image') {
    publish(dockerRegistry, dockerCredential, name, tag)
  }
}

def build(name, tag, variant) {
  sh "blubber deploy/blubber.yaml $variant | docker build -t $name:$tag -f - ."
}

def run(name, tag) {
  docker.image("$name:$tag").run()
}

def publish(registry, credential, name, tag) {
  docker.withRegistry("https://$registry", credential) {
    docker.image("$name:$tag").push(tag)
  }
}
