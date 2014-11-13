import re

tag_re = r'^refs/tags/(.*)'


def set_doc_suffix(item, job, params):
    change = item.change
    docsuffix = ''

    # ref-updated
    # Tags: 'refs/tags/foo'
    # Branch: 'master'
    if hasattr(change, 'ref'):
        tag = re.match(tag_re, change.ref)
        if tag:
            docsuffix = tag.group(1)
        else:
            docsuffix = change.ref
    # Changes
    elif hasattr(change, 'refspec'):
        docsuffix = change.branch

    params['DOC_SUFFIX'] = docsuffix
