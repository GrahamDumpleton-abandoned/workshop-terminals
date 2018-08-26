#!/bin/bash

set -eo pipefail

set -x

URI_ROOT_PATH=${URI_ROOT_PATH:-}

# Add entry to /etc/passwd file.

whoami &> /dev/null || STATUS=$? && true

if [[ "$STATUS" != "0" ]]; then
    echo "Adding passwd file entry for $(id -u)"
    cat /etc/passwd | sed -e "s/^default:/builder:/" > /tmp/passwd
    echo "default:x:$(id -u):$(id -g):,,,:/opt/app-root/src:/bin/bash" >> /tmp/passwd
    cat /tmp/passwd > /etc/passwd
    rm /tmp/passwd
fi

# The butterfly application has a bug whereby if the config file is
# not present, it will ignore the --uri-root-path option, so create
# the file.

mkdir -p $HOME/.config/butterfly
touch $HOME/.config/butterfly/butterfly.conf

# Now execute the program. We need to supply a shell script for the
# shell to setup passwd file intercept using nss_wrapper, and enable
# Python, before executing bash.

env | egrep '^PATH=' > /opt/butterfly/etc/envvars
env | egrep '^KUBERNETES_' >> /opt/butterfly/etc/envvars

oc config set-cluster local --server "https://$KUBERNETES_PORT_443_TCP_ADDR"
oc config set-context me --cluster local --user "$JUPYTERHUB_USER"
oc config use-context me

exec butterfly.server.py --port=8080 \
    --host=0.0.0.0 --uri-root-path="$URI_ROOT_PATH" --unsecure \
    --i-hereby-declare-i-dont-want-any-security-whatsoever \
    --shell=/opt/butterfly/bin/start-terminal.sh
