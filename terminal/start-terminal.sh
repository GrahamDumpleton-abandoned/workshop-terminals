#!/bin/bash

. /opt/app-root/etc/scl_enable

set -a
. /opt/butterfly/etc/envvars
set +a

exec /bin/bash "$@"
