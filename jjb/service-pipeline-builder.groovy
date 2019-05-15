@Library('wikimedia-integration-pipelinelib') import org.wikimedia.integration.*

def builder = new PipelineBuilder(".pipeline/config.yaml")
builder.build(this, params.PLIB_PIPELINE)
