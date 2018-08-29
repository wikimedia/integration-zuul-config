import hudson.plugins.ircbot.v2.IRCConnectionProvider;
import hudson.slaves.OfflineCause
import hudson.util.RemotingDiagnostics

def offlinePercentage = params.OFFLINE_PERCENTAGE.toInteger()
def groovyScript = 'println "df --output=pcent / /srv".execute().text'

def computerNamePrefix = 'integration-slave-'
def offlineMessage = 'Offline due to full partition'

def failed = false
def failedMessage = "Project ${env.JOB_NAME} build ${env.BUILD_NUMBER}"

def diskFull = { diskSize ->
    for (line in diskSize.split('\n')) {
        if (line.startsWith('Use')) {
            continue
        }
        if (line.replaceAll('%', '').toInteger() > offlinePercentage) {
            return true
        }
    }

    return false
}

node('contint1001') {
    try {
        stage('Check agents') {
            for (slave in hudson.model.Hudson.instance.slaves) {
                def computer = slave.computer
                def computerName = computer.getName()

                // Only check nodes that are named like integration-agents
                if (!computerName.startsWith(computerNamePrefix)) {
                    continue
                }

                println "Checking ${computerName}..."

                if (computer.isOffline()) {
                    if (computer.getOfflineCauseReason() == offlineMessage) {
                        println "${computerName} /srv or / FULL! Already offline."
                        failed = true
                    }
                    continue
                }

                def channel = computer.getChannel()
                def diskSize = RemotingDiagnostics.executeGroovy(groovyScript, channel)

                if (diskFull(diskSize)) {
                    println "${computerName} /srv or / FULL! Taking offline..."
                    computer.setTemporarilyOffline(true,
                        new OfflineCause.ByCLI(offlineMessage))
                    failed = true
                }
            }
        }
        stage('Agents are OK') {
            if (failed) {
                currentBuild.result = 'FAILURE'
            }
        }
    } finally {
        stage('Send notifications') {
            def currentResult = currentBuild.result ?: 'SUCCESS'
            def previousResult = currentBuild.previousBuild?.result
            def changed = previousResult != null && previousResult != currentResult
            def isFailure = currentBuild.resultIsWorseOrEqualTo('FAILURE')

            if (isFailure) {

                // First failure
                if (changed) {
                    println "Sending first failure email..."
                    mail to: 'qa-alerts@lists.wikimedia.org',
                        subject: "${failedMessage}: ${currentResult}"
                        body: "${env.BUILD_URL}"
                        attachLog: false
                }
                println "Notifying in IRC"
                IRCConnectionProvider.getInstance().currentConnection().send(
                    '#wikimedia-releng',
                    "${failedMessage}: ${currentResult}"
                )
            }

        }
    }
}
