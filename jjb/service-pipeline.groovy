@Library('wikimedia-integration-pipelinelib') import org.wikimedia.integration.*

node(nodeLabel) {
  def patchset = PatchSet.fromZuul(params)
  def runner = new PipelineRunner(this,
                                  kubeConfig: "/etc/kubernetes/ci-staging.config")
  def testImageID
  def productionImageID
  def gerritComment

  def imageName = params.ZUUL_PROJECT.replaceAll(/\//, '-')
  def imageFullName = runner.qualifyRegistryPath(imageName)
  def timestamp = new Date().format("yyyy-MM-dd-HHmmss", TimeZone.getTimeZone("UTC"))

  def candidateTag = "${timestamp}-candidate"
  def productionTag = "${timestamp}-production"
  def commitSHA = params.ZUUL_COMMIT

  def imageLabels = [
    "zuul.commit": commitSHA,
    "jenkins.job": env.JOB_NAME,
    "jenkins.build": env.BUILD_ID,
  ]

  def imageTags = []

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

    if (testProductionImage && fileExists('.pipeline/helm.yaml')) {
      stage('Test deployment') {
        runner.registerAs(productionImageID, imageName, candidateTag)
        imageTags.add(candidateTag)
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
        imageTags.add(productionTag)

        // Triggered via the publish pipeline when a new tag is pushed
        if (params.ZUUL_REF.startsWith("refs/tags/")) {
          def tagRef = params.ZUUL_REF.substring("refs/tags/".length())
          runner.registerAs(productionImageID, imageName, tagRef)
          imageTags.add(tagRef)
        } else {
          runner.registerAs(productionImageID, imageName, commitSHA)
          imageTags.add(commitSHA)
        }
      }
    }
    currentBuild.result = 'SUCCESS'
  } catch (Exception err) {
    currentBuild.result = 'FAILURE'
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

    if (productionImageID && currentBuild.result == 'SUCCESS') {
      gerritComment = new GerritPipelineComment(
        jobName: env.JOB_NAME,
        buildNumber: env.BUILD_NUMBER,
        jobStatus: currentBuild.result,
        image: imageFullName,
        tags: imageTags
      )
    } else {
      /**
       * If the job is a failure, or if the job was only a test instead of
       * a push to production, then we won't have an image with tags from
       * the registry.
       */
      gerritComment = new GerritPipelineComment(
        jobName: env.JOB_NAME,
        buildNumber: env.BUILD_NUMBER,
        jobStatus: currentBuild.result,
      )
    }

    GerritReview.post(this, gerritComment)
  }
}
