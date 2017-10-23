#!/bin/bash
set -e

case ${1:-missing} in
    config)
        source castor/castor-define-namespace.bash
        ;;
    save)
        source castor/castor-define-namespace.bash
        source castor/castor-save-sync.bash
        ;;
    load)
        source castor/castor-define-namespace.bash
        source castor/castor-load-sync.bash
        ;;
    *)
        echo "USAGE:"
        echo "  castor config"
        echo "  castor save"
        echo "  castor load"
        exit 1
        ;;
esac
