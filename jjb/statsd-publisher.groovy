import java.net.DatagramPacket
import java.net.DatagramSocket
import java.net.InetAddress

def socket = new DatagramSocket()
def address = InetAddress.getByName("statsd.eqiad.wmnet")
def port = 8125

// Sends list of stats as a single UDP request to our statsd server
def sendStat = { stat ->
  stat = "jenkins." + stat
  socket.send(new DatagramPacket(stat.bytes, stat.bytes.length, address, port))
}

def jobName = manager.build.getProject().getName()
def project = "unknown"
def labels = manager.build.getBuiltOn().getAssignedLabels()
def duration = manager.build.getDuration()

def params = manager.build.getBuildVariables()

// Add extra project context if we have it
if (params.containsKey("ZUUL_PROJECT") && params["ZUUL_PROJECT"] != "") {
  project = params["ZUUL_PROJECT"]
}

// Send a timer stat for any "stats-*" labels
labels.findAll { it =~ /^stats-/  }.each { label ->
  sendStat("${label}.${jobName}-${project}:${duration}|ms")
}

