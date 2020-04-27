#!/bin/bash

# irws watcher ansible installation script

function usage {
  echo "
usage:  $0 [options] target
options:        [-v]            ( verbose )
                [-d]            ( very verbose )
                [-l hostname]   ( limit install to 'hostname' )
                [-H]            ( list hosts in the cluster )

target help:    $0 targets
  "
  exit 1
}

function targets {
  echo "
     eval                       Installs to eval hosts (iamtools-test01, 02)
     prod                       Installs to prod hosts (iamtoosl11, 12)
  "
  exit 1
}

# get the base path
dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
base=${dir%/ansible}
cd $dir

playbook=
target=
limit=
verb=0
debug=0
list_hosts=0

# limited args to playbook
while getopts 'h?l:Hvdp:' opt; do
  case "$opt" in
    h) usage
       ;;
    \?) usage
       ;;
    l) limit=$OPTARG
       ;;
    H) listhosts=1
       ;;
    v) verb=1
       ;;
    d) debug=1
       ;;
    p) playbook=$OPTARG
       ;;
  esac
done

shift $((OPTIND-1))
target="$1"
[[ "$target" == "eval" || "$target" == "prod" ]] || usage
[[ -z $playbook ]] && playbook="install-${product}.yml"
echo "Installing $playbook to $target"
[[ -r $playbook ]] || {
  echo "Playbook $playbook not found!"
  exit 1
}

. installer-env/bin/activate
((listhosts>0)) && {
   ansible-playbook ${playbook} --list-hosts -i hosts  --extra-vars "target=${target}"
   exit 0
}

vars=
(( verb>0 )) && vars="$vars -v "
(( debug>0 )) && vars="$vars -vvvv "
[[ -n $limit ]] && {
   [[ $limit == *"."* ]] || limit=${limit}.s.uw.edu
   vars="$vars -l $limit "
}
ansible-playbook ${playbook} $vars -i hosts  --extra-vars "target=${target}"

