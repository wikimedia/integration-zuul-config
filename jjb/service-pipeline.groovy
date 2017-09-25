node('ServicePipeline') {
  def dockerRegistry = 'https://docker-registry.wikimedia.org'
  def dockerCredential = 'docker-registry-uploader'

  def name = params.ZUUL_PROJECT.replaceAll(/\W/, '-')
  def tag = "build-${env.BUILD_ID}"

  def image

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
    image = build(name, tag, 'test')
  }

  stage('Test entry point') {
    image.run()
  }

  stage('Build production image') {
    image = build(name, tag, 'production')
  }

  stage('Register image') {
    docker.withRegistry(dockerRegistry, dockerCredential) {
      image.push("staging-$tag")
    }
  }
}

def build(name, tag, variant) {
  def dockerfile = "Dockerfile.blubber.$variant"
  sh "blubber deploy/blubber.yaml $variant > $dockerfile"
  docker.build("$name:$tag", "-f $dockerfile .")
}
