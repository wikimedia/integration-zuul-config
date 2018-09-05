import hudson.plugins.ircbot.v2.IRCConnectionProvider;
import hudson.slaves.OfflineCause
import hudson.util.RemotingDiagnostics

def offlinePercentage = params.OFFLINE_PERCENTAGE.toInteger()
def disks = ['/', '/srv']
def groovyScript = String.format('println "df %s".execute().text', disks.join(' '))

def computerNamePrefix = 'integration-slave-'

def ircAlerts = []
def jobInfo = "${env.JOB_NAME} build ${env.BUILD_NUMBER}"

class Disk {
    String mount
    int blocks
    int use
    int avail
    int percent
    public String toString() {
        return String.format('%s: %d%%', mount, percent)
    }
}

// Create list disk objects from output of `df`
def newDisksFromDf = { dfOutput ->
    diskObjects = []

    for (line in dfOutput.split('\n')) {
        if (! line) {
            continue
        }

        def parts = line.split()

        if (! parts[1].isInteger()) {
            continue
        }

        def newDisk = new Disk()
        newDisk.mount = parts[5]
        newDisk.blocks = parts[1].toInteger()
        newDisk.use = parts[2].toInteger()
        newDisk.avail = parts[3].toInteger()
        newDisk.percent = parts[4].replace('%', '').toInteger()

        diskObjects.add(newDisk)
    }

    return diskObjects
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
                    if (computer.getOfflineCauseReason().startsWith(env.JOB_NAME)) {
                        println "${computerName} /srv or / FULL! Already offline."
                        ircAlerts.add("${jobInfo} ${computerName}")
                    }
                    continue
                }

                def diskObjects = newDisksFromDf(
                    RemotingDiagnostics.executeGroovy(
                        groovyScript,
                        computer.getChannel()
                    )
                )

                diskObjects.each{ diskObject ->
                    def ircMessage = String.format(
                        '%s %s (%s)',
                        jobInfo,
                        computerName,
                        diskObject.toString()
                    )

                    def jenkinsMessage = String.format(
                        '%s (%s)',
                        jobInfo,
                        diskObject.toString()
                    )

                    println "${jenkinsMessage}"

                    if (diskObject.percent < offlinePercentage) {
                        return
                    }

                    computer.setTemporarilyOffline(
                        true,
                        new OfflineCause.ByCLI(jenkinsMessage)
                    )

                    ircAlerts.add(ircMessage)
                }
            }
        }
    } finally {  // We want notifications regardless of groovy exceptions
        stage('Send notifications') {
            // Alert for computers offline in IRC
            ircAlerts.each { computer ->
                println "${computer}: OFFLINE due to disk space"
                sendIRCAlert("${computer}: OFFLINE due to disk space")
            }

            // Job failed, but no computer is offline *necessarily*
            if (isFailure(currentBuild)) {
                println "Notifying of failure in IRC"
                alertInIRC("${jobInfo}: ${currentBuild.result}")

                // First failure
                if (isFirstFailure(currentBuild)) {
                    println "Sending first failure email..."
                    sendEmailAlert(
                        "${jobInfo}: ${currentBuild.result}",
                        "${env.BUILD_URL}"
                    )
                }
            }
        }
    }
}
