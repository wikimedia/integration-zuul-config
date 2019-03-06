import hudson.plugins.ircbot.v2.IRCConnectionProvider;
import hudson.slaves.OfflineCause
import hudson.util.RemotingDiagnostics

def executionTimeout = params.EXECUTION_TIMEOUT.toInteger()
def cleanupPercentage = params.CLEANUP_PERCENTAGE.toInteger()
def offlinePercentage = params.OFFLINE_PERCENTAGE.toInteger()

def dockerMount = '/var/lib/docker'
def disks = ['/', '/srv', dockerMount]

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

String executeOn = { computer, cmd ->
    RemotingDiagnostics.executeGroovy(
        'print($/' + cmd + '/$.execute().text)',
        computer.getChannel()
    )
}

Map dockerImagesAndTags = { computer ->
    def imagesAndTags = [:]

    executeOn(computer, /docker image ls --format "{{.ID}} {{.Tag}}"/).eachLine {
        def (id, tag) = it.split(' ')

        if (id && tag) {
            imagesAndTags[id] = imagesAndTags[id] ?: []
            imagesAndTags[id] += tag
        }
    }

    imagesAndTags
}

List dockerImagesToRemove = { computer ->
    def imageIDs = []

    dockerImagesAndTags(computer).each { id, tags ->
        if (!tags.contains('latest')) {
            imageIDs += id
        }
    }

    imageIDs
}

def checkDiskSpace = { computer ->
    executeOn(computer, "df ${disks.join(' ')}")
}

def removeDockerImages = { computer ->
    // The 10000 limit on docker rmi arguments is very conservative
    // considering the 2097152 ARG_MAX of our slave instances and the typical
    // 12-character Docker image ID length
    dockerImagesToRemove(computer).collate(10000).each { ids ->
        executeOn(computer, /docker rmi ${ids.join(' ')}/)
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

def isFailure = { build ->
    return build.resultIsWorseOrEqualTo('FAILURE')
}

@NonCPS
def checkAgents = {
    alerts = []
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

                // Don't alert every 5 minutes, it's spammy, try every 25 minutes
                if (env.BUILD_NUMBER.toInteger() % 5 == 0) {
                    alerts.add("${jobInfo} ${computerName}")
                }
            }
            println "${computerName} Offline..."
            continue
        }

        def diskObjects = newDisksFromDf(checkDiskSpace(computer))

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

            if (diskObject.percent >= offlinePercentage) {
                // The offline threshold has been reached
                computer.setTemporarilyOffline(
                    true,
                    new OfflineCause.ByCLI(jenkinsMessage)
                )

                alerts.add(ircMessage)
            } else if (diskObject.percent >= cleanupPercentage && diskObject.mount == dockerMount) {
                // The cleanup threshold for the docker mount has been reached
                removeDockerImages(computer)
            }
        }
    }

    return alerts
}

timeout(executionTimeout) {
    node('contint1001') {
        stage('Check agents') {
            ircAlerts = checkAgents()
        }
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
            }
        }
    }
}
