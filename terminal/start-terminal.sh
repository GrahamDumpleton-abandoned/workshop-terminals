#!/bin/bash

. /opt/app-root/etc/scl_enable

set -a
. /opt/app-root/etc/envvars
set +a

exec /bin/bash "$@"
