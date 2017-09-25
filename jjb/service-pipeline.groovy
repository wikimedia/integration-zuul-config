node('ServicePipeline') {
  def dockerRegistry = 'https://docker-registry.wikimedia.org'
  def dockerCredential = 'wmf-docker-uploader'

  def name
  def tag
  def image

  stage('Setup') {
    checkout scm
    name = npmPackageName()
    tag = env.BUILD_ID
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

def build = { name, tag, variant ->
  def dockerfile = blubber(variant)
  docker.build("$name:$tag", "-f $dockerfile .")
}

String blubber = { variant ->
  def dockerfile = "Dockerfile.blubber.$variant"
  sh "blubber deploy/blubber.yaml $variant > $dockerfile"
  dockerfile
}

String npmPackageName = {
  def cmd = 'npm run env | awk -F \'=\' \'$1 == "npm_package_name" { print $2 }\''
  sh(returnStdout: true, script: cmd).trim()
}
