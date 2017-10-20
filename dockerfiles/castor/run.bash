#!/bin/bash
set -e

case ${1:-missing} in
    clear)
        find /cache -mindepth 1 -delete
        ;;
    config)
        source castor/castor-define-namespace.bash
        ;;
    load)
        source castor/castor-define-namespace.bash
        source castor/castor-load-sync.bash
        ;;
    *)
        echo "USAGE:"
        echo "  castor config: show the castor namespace"
        echo "  castor load: restore from central cache"
        exit 1
        ;;
esac
