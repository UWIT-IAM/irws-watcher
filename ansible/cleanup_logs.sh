#!/bin/bash

# clean various collection directories
# this should run monthly by cron

# drop old process logs
cd /logs/irws-watcher
(( $? > 0 )) && exit 1
find . -maxdepth 1 -name 'process.log*' -mtime +90 -delete
find . -maxdepth 1 -name 'audit.log*' -mtime +90 -delete
find . -maxdepth 1 -name 'eval-process.log*' -mtime +90 -delete
find . -maxdepth 1 -name 'eval-audit.log*' -mtime +90 -delete

