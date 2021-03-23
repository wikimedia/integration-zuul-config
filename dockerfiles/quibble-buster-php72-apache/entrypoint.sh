#!/bin/bash

set -euxo pipefail

/usr/bin/supervisord -c /etc/supervisor/supervisord.conf
exec /usr/local/bin/quibble --web-backend=external --web-url=http://127.0.0.1:9413 "$@"
