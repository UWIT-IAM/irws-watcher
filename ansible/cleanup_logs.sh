#!/bin/bash

# clean various collection directories
# this should run monthly by cron

# irws recons
cd {{app_base}}/workday/apps/irws_recon
find . -maxdepth 1 -name 'recon.*.dat' -mtime +30 -delete

# logs

cd {{app_base}}/log

# drop old process logs
find . -maxdepth 1 -name 'process.log*' -mtime +30 -delete

# roll over run logs
for LOG in recon.run.log roles.run.log
do
  (( ln = 12 ))
  while (( ln > 0 ))
  do
     (( nln = ln - 1 ))
     [[ -r ${LOG}.${nln} ]] && mv ${LOG}.${nln} ${LOG}.${ln}
     (( ln = nln ))
  done
  [[ -r ${LOG} ]] && mv ${LOG} ${LOG}.1
done

