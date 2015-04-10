import re

debian_branch_re = r'^debian/(.*)'


def set_distributions(item, job, params):
    distributions = []
    change = item.change

    if hasattr(change, 'branch'):
        debian_branch = re.match(debian_branch_re, change.branch)
        if debian_branch:
            distributions.append(debian_branch.group(1))

    if not distributions:
        distributions = ['sid']
    params['DEBIAN_GLUE_DISTRIBUTIONS'] = ' '.join(distributions)
