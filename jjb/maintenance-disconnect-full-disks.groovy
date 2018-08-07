import hudson.slaves.OfflineCause
import hudson.util.RemotingDiagnostics

def env = System.getenv()
def offlinePercentage = env['OFFLINE_PERCENTAGE'].toInteger()

def groovyScript = 'println "df --output=pcent /srv".execute().text'

def diskFull = { diskSize ->
    for (line in diskSize.split('\n')) {
        if (line.startsWith('Use')) {
            continue
        }
        return line.replaceAll('%', '').toInteger() > offlinePercentage
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
