#!/bin/bash

# verify something

cd /data/local/irws-watcher/apps
umask 002

. /data/local/irws-watcher/env/bin/activate

help=
[[ -z "$1" ]] && help=--help
python verify.py $help $*

