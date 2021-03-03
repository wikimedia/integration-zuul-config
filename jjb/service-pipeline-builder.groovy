@Library('wikimedia-integration-pipelinelib') import org.wikimedia.integration.*

import groovy.json.JsonSlurperClassic

@NonCPS
def parseJson(jsonString) {
  def jsonSlurper = new JsonSlurperClassic()

  jsonSlurper.parseText(jsonString)
}

def globalAllowedCredentials = parseJson('''{{ globalAllowedCredentials | default({}) | tojson }}''')
def pipelineAllowedCredentials = parseJson('''{{ allowedCredentials | default({}) | tojson }}''')

def allowedCredentials = globalAllowedCredentials + pipelineAllowedCredentials

def builder = new PipelineBuilder([allowedCredentials: allowedCredentials], ".pipeline/config.yaml")
builder.build(this, params.PLIB_PIPELINE)
