import hudson.util.RemotingDiagnostics
import hudson.slaves.OfflineCause;

def groovyScript = 'println "df --output=pcent /srv".execute().text'

def diskFull = { diskSize ->
    for (line in diskSize.split('\n')) {
        if (line.startsWith('Use')) {
            continue
        }
        return line.replaceAll('%', '').toInteger() > 95
    }

    return false
}

node('master') {
    for (slave in hudson.model.Hudson.instance.slaves) {
        def compuer = slave.computer

        if (computer.isOffline()) {
            continue
        }

        def channel = computer.getChannel()
        def diskSize = RemotingDiagnostics.executeGroovy(groovyScript, channel)

        if (diskFull(diskSize)) {
            computer.setTemporarilyOffline(true,
                new OfflineCause.ByCLI("Offline due to /srv/ being filled"))
        }
    }
}
