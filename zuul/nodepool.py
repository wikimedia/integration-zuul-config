

# Instruct Jenkins Gearman plugin to put a node offline on job completion.
# Ie for nodepool
def offline_when_complete(item, job, params):
    params['OFFLINE_NODE_WHEN_COMPLETE'] = '1'
