# Utility IRWS message handler

## Activity

* watch uwnetid messages for affiliation changes
* watch source messages for PAC needs

## Installaiton

* This is for python3
* IRWS messages are type UWIT-1 and require the uwit-1 branch of messagetools
* Resttools branch 'python3' must be used.
* For the Ansible installer 
** pip install ansible

## Test

* run pytest in this directory

## Style
* pycodesytle --max-line-length=160

