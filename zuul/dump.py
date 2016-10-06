import sys

from parameter_functions import get_dependencies
from parameter_functions import dependencies


def dumpit(repo, dependencies):
    print "== " + repo + " =="
    print ("\n").join(
        sorted(get_dependencies(repo, dependencies))
    )
    print

if len(sys.argv) == 2 and sys.argv[1]:
    dumpit(sys.argv[1], dependencies)

else:
    for repo in dependencies:
        dumpit(repo, dependencies)
