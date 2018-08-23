#!/bin/bash

set -x

URI_ROOT_PATH=${URI_ROOT_PATH:-/}

exec butterfly.server.py --port=8080 --host=0.0.0.0 \
    --debug --uri-root-path="$URI_ROOT_PATH" --unsecure \
    --i-hereby-declare-i-dont-want-any-security-whatsoever
