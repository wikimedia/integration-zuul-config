class FakeChange(object):

    def __init__(self, branch, ref=None, refspec=None):
        self.branch = branch
        if ref:
            self.ref = ref
        if refspec:
            self.refspec = refspec


class FakeItemChange(object):

    def __init__(self, *args, **kwargs):
        self.change = FakeChange(*args, **kwargs)


class FakeJob(object):

    def __init__(self, name):
        self.name = name
