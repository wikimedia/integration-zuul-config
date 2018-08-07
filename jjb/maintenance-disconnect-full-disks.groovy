import hudson.slaves.OfflineCause
import hudson.util.RemotingDiagnostics

def offlinePercentage = params.OFFLINE_PERCENTAGE.toInteger()

def groovyScript = 'println "df --output=pcent /srv".execute().text'

// Only check certain machines
def computerNamePrefix = 'integration-slave-'

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
    for (slave in hudson.model.Hudson.instance.slaves) {
        def computer = slave.computer
        def computerName = computer.getName()

        // Only check nodes that are online and are integration agents
        if (!computerName.startsWith(computerNamePrefix) || computer.isOffline()) {
            continue
        }

        println "Checking ${computerName}..."

        def channel = computer.getChannel()
        def diskSize = RemotingDiagnostics.executeGroovy(groovyScript, channel)

        if (diskFull(diskSize)) {
            println "${computerName} /srv FULL! Taking offline..."
            computer.setTemporarilyOffline(true,
                new OfflineCause.ByCLI("Offline due to /srv/ being filled"))
        }
    }
}
