import hudson.util.RemotingDiagnostics

def groovy_script = 'println "df --output=pcent /srv".execute().text'

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
        def diskSize = RemotingDiagnostics.executeGroovy(groovy_script, channel)

        if (diskFull(diskSize)) {
            computer.disconnect()
        }
    }
}
