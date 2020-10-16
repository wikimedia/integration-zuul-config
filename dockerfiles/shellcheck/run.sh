#!/bin/bash

set -euxo pipefail

cd /src

# Run against all scripts with a /bin/bash or /bin/sh shebang
grep -RE '#!/bin/(ba)?sh' ** -l | xargs -n1 -exec shellcheck
