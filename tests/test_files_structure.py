import os
import unittest


class TestFilesStructure(unittest.TestCase):

    def test_have_no_tabs(self):
        root_dir = os.path.dirname(os.path.dirname(__file__))
        for root, dirs, files in os.walk(root_dir):
            for name in files:
                if name.endswith(('.pyc', '.gpg')):
                    # Dunno why these files contain tabs
                    continue
                fname = os.path.join(root, name)
                with open(fname) as f:
                    if '\t' in f.read():
                        raise AssertionError('%s has tabs' % fname)
            for name in dirs:
                if name.startswith(('.', '__pycache__')):
                    dirs.remove(name)
