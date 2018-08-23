#!/bin/bash

set -x

URI_ROOT_PATH=${URI_ROOT_PATH:-}

# The butterfly application has a bug whereby if the config file is
# not present, it will ignore the --uri-root-path option, so create
# the file.

mkdir -p $HOME/.config/butterfly
touch $HOME/.config/butterfly/butterfly.conf

# Now execute the program. We need to supply a shell script for the
# shell to setup passwd file intercept using nss_wrapper, and enable
# Python, before executing bash.

exec butterfly.server.py --port=8080 --host=0.0.0.0 \
    --uri-root-path="$URI_ROOT_PATH" --unsecure \
    --i-hereby-declare-i-dont-want-any-security-whatsoever \
    --shell=/opt/app-root/bin/start-terminal.sh
