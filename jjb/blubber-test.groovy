@Library('wikimedia-integration-pipelinelib') import org.wikimedia.integration.*

node('ServicePipelineK8s') {
  def patchset = PatchSet.fromZuul(params)
  def runner = new PipelineRunner(this)
  def imageID

  stage('Checkout patch') {
    checkout(patchset.getSCM())
  }

  stage('Build image') {
    imageID = runner.build('test')
  }

  stage('Run tests') {
    runner.run(imageID)
  }
}
