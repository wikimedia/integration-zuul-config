def set_php_bin(item, job, params):
    """
    Sets a $PHP_BIN variable based on the job name
    :type item: zuul.model.QueueItem
    :type job: zuul.model.Job
    :type params: dict
    """
    if 'php55' in job.name:
        params['PHP_BIN'] = 'php5'
