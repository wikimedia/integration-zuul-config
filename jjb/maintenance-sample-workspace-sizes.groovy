import hudson.util.RemotingDiagnostics

import java.io.File

def executionTimeout = params.EXECUTION_TIMEOUT_SECONDS.toInteger()
def targetNode = params.TARGET_NODE

def computerNamePrefix = 'integration-agent-docker-'
def image = 'docker-registry.wikimedia.org/releng/ci-stretch'
def metricsServer = 'graphite-in.eqiad.wmnet'

String executeOn(computer, cmd) {
    RemotingDiagnostics.executeGroovy(
        'print($/' + cmd + '/$.execute().text)',
        computer.getChannel()
    )
}


// Key is job name, value is largest seen workspace size (bytes, as a double)
def workspaceSize = [:]

def recordWorkspaceSize = { job, size ->
    def currentMax = workspaceSize[job]
    if (currentMax == null || size > currentMax) {
        workspaceSize[job] = size
    }
}

// Returns a string
def workspaceDirectoryToJobName = { dir ->
    def basename = new File(dir).getName()

    def atpos = basename.indexOf('@')
    if (atpos == -1) {
        return basename
    } else {
        return basename.substring(0, atpos)
    }
}

def processDuOutput = { output ->
    output.split('\n').collect {
        def parts = it.split(/\s+/)
        def job = workspaceDirectoryToJobName(parts[1])
        def size = parts[0].toDouble() * 1024

        recordWorkspaceSize(job, size)
    }
}


def checkAgent = { computer ->
    processDuOutput(executeOn(computer, "docker run --rm --init -v /srv/jenkins/workspace/workspace:/workspaces ${image} find /workspaces -mindepth 1 -maxdepth 1 -type d -exec du -s {} ; "))
}

def shouldOperate = { computerName ->
    // If we got a specific target node,
    if (targetNode) {
        return computerName == targetNode
    } else {
        return computerName.startsWith(computerNamePrefix)
    }
}

def reportMetrics = {
    def now = (new Date().getTime() / 1000).toInteger()
    def conn = new Socket(metricsServer, 2003)

    workspaceSize.each { job, size ->
        def data = "jenkins.job.${job}.workspace-size ${size} ${now}\n"
        //println "Sending ${data}"
        conn << data
    }
    
    conn.close()
}

def checkAgents = {
    for (worker in hudson.model.Hudson.instance.slaves) {
        def computer = worker.computer
        def computerName = computer.getName()

        if (shouldOperate(computerName)) {
            println "Checking ${computerName}..."
            checkAgent(computer)
        }
    }
}

timestamps {
    timeout(time: executionTimeout, unit: 'SECONDS') {
        node('contint2001') {
            stage('Check agents') {
                checkAgents()
            }
            stage('Report metrics') {
                reportMetrics()
            }
        }
    }
}
