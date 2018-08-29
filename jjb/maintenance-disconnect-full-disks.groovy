import hudson.plugins.ircbot.v2.IRCConnectionProvider;
import hudson.slaves.OfflineCause
import hudson.util.RemotingDiagnostics

def offlinePercentage = params.OFFLINE_PERCENTAGE.toInteger()
def groovyScript = 'println "df --output=pcent / /srv".execute().text'

def computerNamePrefix = 'integration-slave-'
def offlineMessage = 'Offline due to full partition'

def failedComputers = []
def failedMessage = "${env.JOB_NAME} build ${env.BUILD_NUMBER}"

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

def sendIRCAlert = { message ->
    IRCConnectionProvider.getInstance().currentConnection().send(
        '#wikimedia-releng',
        message
    )
}

def sendEmailAlert = { subject, body ->
    mail to: 'qa-alerts@lists.wikimedia.org',
        subject: subject,
        body: body,
        attachLog: false
}

def isFailure = { build ->
    return build.resultIsWorseOrEqualTo('FAILURE')
}

def isFirstFailure = { build ->
    if (! isFailure(build)) {
        return false
    }
    def currentResult = currentBuild.result ?: 'SUCCESS'
    def previousResult = currentBuild.previousBuild?.result
    return previousResult != null && previousResult != currentResult
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
                        failedComputers.add(computerName)
                    }
                    continue
                }

                def channel = computer.getChannel()
                def diskSize = RemotingDiagnostics.executeGroovy(groovyScript, channel)

                if (diskFull(diskSize)) {
                    println "${computerName} /srv or / FULL! Taking offline..."
                    computer.setTemporarilyOffline(true,
                        new OfflineCause.ByCLI(offlineMessage))
                    failedComputers.add(computerName)
                }
            }
        }
    } finally {  // We want notifications regardless of groovy exceptions
        stage('Send notifications') {
            // Alert for computers offline in IRC
            failedComputers.each {
                sendIRCAlert("${failedMessage} - ${it}: OFFLINE due to disk space")
            }

            // Job failed, but no computer is offline *necessarily*
            if (isFailure(currentBuild)) {
                println "Notifying in IRC"
                alertInIRC("${failedMessage}: ${currentResult}")

                // First failure
                if (isFirstFailure(currentBuild)) {
                    println "Sending first failure email..."
                    sendEmailAlert(
                        "${failedMessage}: ${currentResult}",
                        "${env.BUILD_URL}"
                    )
                }
            }
        }
    }
}
