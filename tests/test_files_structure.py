import pytest
import subprocess


def test_have_no_tabs():
    with pytest.raises(subprocess.CalledProcessError) as e:
        subprocess.check_call([
            'git', 'grep', '-n', '-I', '-P', '\t'])
        pytest.fail('A file has tabs, see stdout for details')
    assert 1 == e.value.returncode, 'when there is no tabs: git grep exit 1'
