#!/bin/bash

exec butterfly.server.py --unsecure --port=8080 --host=0.0.0.0 \
    --i-hereby-declare-i-dont-want-any-security-whatsoever
