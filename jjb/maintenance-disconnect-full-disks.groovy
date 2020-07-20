import hudson.plugins.ircbot.v2.IRCConnectionProvider;
import hudson.slaves.OfflineCause
import hudson.util.RemotingDiagnostics

def executionTimeout = params.EXECUTION_TIMEOUT_SECONDS.toInteger()
def cleanupPercentage = params.CLEANUP_PERCENTAGE.toInteger()
def offlinePercentage = params.OFFLINE_PERCENTAGE.toInteger()
def targetNode = params.TARGET_NODE

def computerNamePrefix = 'integration-agent-'
def masterName = 'contint2001'

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

String executeOn(computer, cmd) {
    RemotingDiagnostics.executeGroovy(
        'print($/' + cmd + '/$.execute().text)',
        computer.getChannel()
    )
}

def dockerMount = { computerName ->
    switch(computerName) {
        case masterName:
            return '/mnt/docker'
        default:
            return '/var/lib/docker'
    }
}

def disks = { computerName ->
    ['/', '/srv', dockerMount(computerName)].toSet()
}

Map dockerImagesAndTags(computer) {
    def imagesAndTags = [:]

    def output = executeOn(computer, /docker image ls --format {{.ID}}:{{.Tag}}/)
    def lines = output.tokenize("\n")

    for (int i = 0; i < lines.size; i++ ) {
        def it = lines[i]
        def (id, tag) = it.split(':')

        if (id && tag) {
            imagesAndTags[id] = imagesAndTags[id] ?: []
            imagesAndTags[id] += tag
        }
    }

    imagesAndTags
}

List dockerImagesToRemove(computer) {
    def imageIDs = []

    println "Scanning docker images on ${computer.getName()}"
    dockerImagesAndTags(computer).each { id, tags ->
        if (!tags.contains('latest')) {
            imageIDs += id
        }
    }

    imageIDs
}

def checkDiskSpace = { computer, mountPoints ->
    executeOn(computer, "df ${mountPoints.join(' ')}")
}

def removeDockerImages = { computer ->
    // The 10000 limit on docker rmi arguments is very conservative
    // considering the 2097152 ARG_MAX of our worker instances and the typical
    // 12-character Docker image ID length
    dockerImagesToRemove(computer).collate(10000).each { ids ->
        def idsJoin = ids.join(' ')
        println "Removing images: ${idsJoin}"
        executeOn(computer, /docker rmi ${idsJoin}/)
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

def shouldOperate = { computerName ->
    // If we got a specific target node,
    if (targetNode) {
      return computerName == targetNode
    }

    // Fire for nodes named like integration-agents or master:
    return computerName.startsWith(computerNamePrefix) || (computerName == masterName)
}

@NonCPS
def checkAgents = {
    alerts = []
    for (worker in hudson.model.Hudson.instance.slaves) {
        def computer = worker.computer
        def computerName = computer.getName()
        def isMaster = computerName == masterName

        if (! shouldOperate(computerName)) {
            continue
        }

        println "Checking ${computerName}..."

        def diskObjects = newDisksFromDf(
            checkDiskSpace(computer, disks(computerName))
        )

        def complaints = []
        diskObjects.each{ diskObject ->
            def debugMessage = String.format(
                '%s %s (%s)',
                jobInfo,
                computerName,
                diskObject.toString()
            )

            println debugMessage
            if (diskObject.percent >= cleanupPercentage && diskObject.mount == dockerMount(computerName)) {
                println "Cleanup threshold for Docker mount has been reached"
                removeDockerImages(computer)

                // Re-check disk space for docker mount, after cleanup, and update IRC
                // message:
                diskObject = newDisksFromDf(checkDiskSpace(computer, [diskObject.mount]))[0]
                debugMessage = String.format(
                    '%s %s (%s)',
                    jobInfo,
                    computerName,
                    diskObject.toString()
                )
                println "Post-Docker-cleanup: ${debugMessage}"
            }

            if (diskObject.percent >= offlinePercentage) {
                complaints.add(diskObject)
            }
        }

        def message = String.format(
            '%s %s (%s)',
            jobInfo,
            computerName,
            diskObjects.collect { it.toString() }.join(', ')
        )

        // If we have any complaints, take action.
        if (complaints.size() > 0) {
            if (computer.isOffline()) {
                println "${computerName} Already offline - taking no action"
                // Don't alert every 5 minutes, it's spammy, try every 25 minutes
                if (env.BUILD_NUMBER.toInteger() % 5 == 0) {
                    alerts.add(message + ": still OFFLINE due to disk space")
                }
            } else if (!isMaster) {
                message = message + ": OFFLINE due to disk space"
                // Don't take the master node offline, we need it
                println "Offline threshold has been reached"
                computer.setTemporarilyOffline(
                    true,
                    new OfflineCause.ByCLI(message)
                )
                alerts.add(message)
            }
        } else {
            // Disk space is ok, so we should be online
            if (computer.getOfflineCauseReason().startsWith(env.JOB_NAME)) {
                message = message + ": RECOVERY disk space OK"
                println "Disk space within norms - bringing ${computerName} online"
                computer.setTemporarilyOffline(false, null)
                alerts.add(message)
            }
        }
    }

    return alerts
}

timestamps {
    timeout(time: executionTimeout, unit: 'SECONDS') {
        node('contint2001') {
            stage('Check agents') {
                println "Cleanup percentage: ${cleanupPercentage}"
                println "Offline percentage: ${offlinePercentage}"
                ircAlerts = checkAgents()
            }
            stage('Send notifications') {
                // Alert for computers offline in IRC
                ircAlerts.each { message ->
                    println message
                    sendIRCAlert(message)
                }

                // Job failed, but no computer is offline *necessarily*
                if (isFailure(currentBuild)) {
                    println "Notifying of failure in IRC"
                    alertInIRC("${jobInfo}: ${currentBuild.result}")
                }
            }
        }
    }
}
