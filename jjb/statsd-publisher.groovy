import java.net.DatagramPacket
import java.net.DatagramSocket
import java.net.InetAddress

def socket = new DatagramSocket()
def address = InetAddress.getByName("statsd.eqiad.wmnet")
def port = 8125

// Sends list of stats as a single UDP request to our statsd server
def sendStats = { stats ->
  // See format at https://github.com/etsy/statsd/blob/master/docs/metric_types.md
  def payload = stats.collect {
    "jenkins." + it[0].join(".") + ":" + it[1] + "|" + it[2..-1].join("|")
  }.join("\n").bytes

  socket.send(new DatagramPacket(payload, payload.length, address, port))
}

def jobName = manager.build.getProject().getName()
def project = "unknown"
def node = manager.build.getBuiltOn().getNodeName()
def labels = manager.build.getBuiltOn().getAssignedLabels()
def duration = manager.build.getDuration()

def params = manager.build.getBuildVariables()

// Add extra project context if we have it
if (params.containsKey("ZUUL_PROJECT") && params["ZUUL_PROJECT"] != "") {
  project = params["ZUUL_PROJECT"]
}

// Send separate pairs of counts/timers with context by job, node, and node label
def stats = [
  [["job", jobName, project, "builds"], 1, "c"],
  [["job", jobName, project, "duration"], duration, "ms"],
  [["node", node, "job", jobName, project, "builds"], 1, "c"],
  [["node", node, "job", jobName, project, "duration"], duration, "ms"],
]

labels.each { label ->
  stats.add([["label", label, "job", jobName, project, "builds"], 1, "c"])
  stats.add([["label", label, "job", jobName, project, "duration"], duration, "ms"])
}

sendStats(stats)
