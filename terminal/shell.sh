#!/bin/bash

. /opt/app-root/etc/generate_container_user
. /opt/app-root/etc/scl_enable

exec /bin/bash "$@"
