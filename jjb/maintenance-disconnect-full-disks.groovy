import hudson.slaves.OfflineCause
import hudson.util.RemotingDiagnostics

def offlinePercentage = params.OFFLINE_PERCENTAGE.toInteger()
def groovyScript = 'println "df --output=pcent /srv".execute().text'

def computerNamePrefix = 'integration-slave-'
def offlineMessage = 'Offline due to /srv/ being filled'

def failed = false

def diskFull = { diskSize ->
    for (line in diskSize.split('\n')) {
        if (line.startsWith('Use')) {
            continue
        }
        return line.replaceAll('%', '').toInteger() > offlinePercentage
    }

    return false
}

node('contint1001') {
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
                    println "${computerName} /srv FULL! Already offline."
                    failed = true
                }
                continue
            }

            def channel = computer.getChannel()
            def diskSize = RemotingDiagnostics.executeGroovy(groovyScript, channel)

            if (diskFull(diskSize)) {
                println "${computerName} /srv FULL! Taking offline..."
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
}
