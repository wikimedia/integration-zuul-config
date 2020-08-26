import os.path
import shutil
import subprocess
import tempfile
import unittest

SCRIPT = os.path.join(
    os.path.dirname(__file__),
    '../ci-common/content/ci-src-setup.sh')


class Test(unittest.TestCase):

    fixture_dir = None
    upstream = None
    workspace = None

    @classmethod
    def setUpClass(cls):
        cls.fixture_dir = tempfile.mkdtemp()
        cls.upstream = os.path.join(cls.fixture_dir, 'upstream')
        cls.workspace = os.path.join(cls.fixture_dir, 'workspace')

        # Wrapper to ensure a commit has an author
        def git_commit(*args):
            return [
                'git',
                '-c', 'user.name=Jane',
                '-c', 'user.email=jane@example.org',
                'commit'] + list(args)

        git_cmds = [
            ['git', 'init'],
            git_commit('--allow-empty', '-m', 'first commit'),
            # Add submodule to itself
            ['git', 'submodule', '--quiet', 'add',
                '--', cls.upstream, 'submodule'],
            git_commit('-a', '-m', 'add submodule'),
            git_commit('--allow-empty', '-m', 'second commit'),
            ['git', 'tag', 'v1.0', 'HEAD'],
            git_commit('--allow-empty', '-m', 'third commit'),

        ]
        os.mkdir(cls.upstream)
        for git_cmd in git_cmds:
            subprocess.check_output(git_cmd, cwd=cls.upstream)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.fixture_dir)

    def setUp(self):
        self.wipe_workspace()
        os.mkdir(self.workspace)

    def tearDown(self):
        self.wipe_workspace()

    def wipe_workspace(self):
        shutil.rmtree(self.workspace, ignore_errors=True)

    def run_script(self, env):
        # With some sane defaults
        run_env = {
            'ZUUL_URL': self.fixture_dir,
            'ZUUL_PROJECT': self.upstream[len(self.fixture_dir) + 1:],
            }
        run_env.update(env)

        print("TEST DEBUG> running %s" % os.path.basename(SCRIPT))
        proc = subprocess.Popen(
            [SCRIPT],
            cwd=self.workspace, env=run_env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)
        # Nose can not capture output from check_call / check_output, thus
        # print it and it will happilly capture it.
        # read() is until EOF, there is thus no need to wait().
        print(proc.stdout.read())
        print("TEST DEBUG> done running %s" % os.path.basename(SCRIPT))

    def assertGitOutput(self, expected, command, msg=None):
        if type(command) == str:
            command = [command]

        git_cmd = ['git']
        git_cmd.extend(command)

        actual = subprocess.check_output(git_cmd, cwd=self.workspace)
        self.assertEqual(expected, actual, msg=msg)

    def test_checkouts_to_a_named_local_branch(self):
        self.run_script({
            'ZUUL_BRANCH': 'master',
            'ZUUL_REF': 'master',
            'GIT_NO_SUBMODULES': '1',
        })
        self.assertGitOutput(
            'refs/heads/master\n',
            ['rev-parse', '--symbolic-full-name', 'HEAD'])

    def test_can_skip_submodule_processing(self):
        self.run_script({
            'ZUUL_REF': 'master',
            'ZUUL_BRANCH': 'master',
            'GIT_NO_SUBMODULES': '1',
            })
        self.assertListEqual(
            [],
            os.listdir(os.path.join(self.workspace, 'submodule'))
        )

    def test_default_to_process_submodules(self):
        self.run_script({
            'ZUUL_REF': 'master',
            'ZUUL_BRANCH': 'master',
            })
        self.assertGitOutput(
            'first commit',
            ['submodule', '--quiet', 'foreach',
                'git', 'log', '--pretty=format:%s'],
            )
