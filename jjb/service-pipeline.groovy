@Library('wikimedia-integration-pipelinelib') import org.wikimedia.integration.*

node(nodeLabel) {
  def patchset = PatchSet.fromZuul(params)
  def runner = new PipelineRunner(this)
  def imageID

  def imageName = params.ZUUL_PROJECT.replaceAll(/\//, '-')
  def timestamp = new Date().format("yyyyMMddHHmmss", TimeZone.getTimeZone("UTC"))

  def candidateTag = "${timestamp}-candidate"
  def productionTag = "${timestamp}-production"

  def imageLabels = [
    "zuul.commit": params.ZUUL_COMMIT,
    "jenkins.job": env.JOB_NAME,
    "jenkins.build": env.BUILD_ID,
  ]

  stage('Checkout patch') {
    checkout(patchset.getSCM())
  }

  stage('Build test image') {
    imageID = runner.build('test', imageLabels)
  }

  stage('Run test image') {
    try {
      runner.run(imageID)
    } finally {
      // Clean up test images on production machines
      if (pushProductionImage) {
        runner.removeImage(imageID)
      }
    }
  }

  if (testProductionImage || pushProductionImage) {
    stage('Build candidate image') {
      imageID = runner.build('production', imageLabels)
    }
  }

  if (testProductionImage) {
    stage('Test deployment') {
      runner.registerAs(imageID, imageName, candidateTag)
      def release = runner.deploy(imageName, candidateTag)

      try {
        runner.testRelease(release)
      } catch (exception) {
        runner.removeImage(imageID)
        throw exception
      } finally {
        runner.purgeRelease(release)
      }
    }
  }

  if (pushProductionImage) {
    stage('Register production image') {
      try {
        runner.registerAs(imageID, imageName, productionTag)
      } finally {
        runner.removeImage(imageID)
      }
    }
  }
}
