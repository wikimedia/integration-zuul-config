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
}

def labels = manager.build.getBuiltOn().getAssignedLabels()
def duration = manager.build.getDuration()

// Send a timer stat for any "stats-*" labels on the node
labels.findAll { it =~ /^stats-/  }.each { label ->
  sendStat("${label}:${duration}|ms")
}

