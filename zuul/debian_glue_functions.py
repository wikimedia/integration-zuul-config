import re

debian_branch_re = r'^debian/(.*)'


def set_distributions(item, job, params):
    """
    Set the distributions to build the patch against

    Recognize branches 'debian/(.*)'. Hence a patch sent against the branch
    debian/jessie-wikimedia will have the job build against the distribution
    named 'jessie-wikimedia'.

    TODO: add a map lookup to be able to build a (project,branch) against
    multiples distributions.

    Fallback: 'sid'
    """
    distributions = []
    change = item.change

    if hasattr(change, 'branch'):
        debian_branch = re.match(debian_branch_re, change.branch)
        if debian_branch:
            distributions.append(debian_branch.group(1))

    if not distributions:
        distributions = ['sid']
    params['DEBIAN_GLUE_DISTRIBUTIONS'] = ' '.join(distributions)
