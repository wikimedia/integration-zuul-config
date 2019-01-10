import json
import urllib2

JENKINS_API_JOBS_URL = \
    'https://integration.wikimedia.org/ci/api/json?pretty=true&tree=jobs[name]'

req = urllib2.urlopen(JENKINS_API_JOBS_URL)
result = json.load(req)

print("\n".join([job.get('name') for job in result.get('jobs')]))
