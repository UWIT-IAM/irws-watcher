#!/bin/bash

# verify something

cd /data/local/irws-watcher/apps
umask 002

. /data/local/irws-watcher/env/bin/activate

while :;
do
   python activity_watcher.py $*
   sleep 5
done

