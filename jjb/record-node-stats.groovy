import java.net.DatagramPacket
import java.net.DatagramSocket
import java.net.InetAddress

def socket = new DatagramSocket()
def address = InetAddress.getByName("labmon1001.eqiad.wmnet")
def port = 8125

// Sends list of stats as a single UDP request to our statsd server
def sendStat = { stat ->
  stat = "jenkins." + stat
  socket.send(new DatagramPacket(stat.bytes, stat.bytes.length, address, port))
  manager.listener.logger.println("sent stat '${stat}' to '${address}:${port}'")
}

// See https://issues.jenkins-ci.org/browse/JENKINS-42952 for why
// manager.build.duration can't be used here.
def duration = System.currentTimeMillis() - manager.build.startTimeInMillis

// Send a timer stat for any "stats-*" labels on the node
def labels = manager.build.getBuiltOn().getAssignedLabels().findAll { it =~ /^stats-/  }

if (labels.size() < 1) {
  manager.listener.logger.println("no 'stats-*' labels configured for this node")
} else {
  labels.each { label ->
    sendStat("${label}:${duration}|ms")
  }
}
