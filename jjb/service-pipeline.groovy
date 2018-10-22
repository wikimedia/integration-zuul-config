@Library('wikimedia-integration-pipelinelib') import org.wikimedia.integration.*

node(nodeLabel) {
  def patchset = PatchSet.fromZuul(params)
  def runner = new PipelineRunner(this,
                                  kubeConfig: "/etc/kubernetes/ci-staging.config",
                                  registry: dockerRegistry)
  def testImageID
  def productionImageID

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

  try {
    stage('Build test image') {
      testImageID = runner.build('test', imageLabels)
    }

    stage('Run test image') {
      runner.run(testImageID)
    }

    if (testProductionImage || pushProductionImage) {
      stage('Build candidate image') {
        productionImageID = runner.build('production', imageLabels)
      }
    }

    if (testProductionImage) {
      stage('Test deployment') {
        runner.registerAs(productionImageID, imageName, candidateTag)
        def release = runner.deploy(imageName, candidateTag)

        try {
          runner.testRelease(release)
        } catch (exception) {
          runner.removeImage(productionImageID)
          throw exception
        } finally {
          runner.purgeRelease(release)
        }
      }
    }

    if (pushProductionImage) {
      stage('Register production image') {
        runner.registerAs(productionImageID, imageName, productionTag)
      }
    }
  } finally {
    // Clean up test images on production machines
    if (pushProductionImage) {
      if (testImageID) {
        runner.removeImage(testImageID)
      }

      if (productionImageID) {
        runner.removeImage(productionImageID)
      }
    }
  }
}
