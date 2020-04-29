import os

RUN_MODE = 'Test'
SETTINGS_NAME = 'Test configuration'
settings_path = os.path.dirname(os.path.abspath(__file__))

DEFAULT_CERT_FILE = '../certs/test-2048.crt'
DEFAULT_KEY_FILE = '../certs/test-2048.key'
DEFAULT_CA_FILE = '../certs/test-ca.crt'

FILTER_FILE = settings_path + '/data/PersonRegGroupDefs.xml'

GWS_CONF = {
    'HOST':  'https://some-server.uw.edu',
    'SOCKET_TIMEOUT':  900.0,
}

IRWS_CONF = {
    'HOST':  'https://some-server.u.washington.edu',
    'SERVICE_NAME': 'registry',
    'SOCKET_TIMEOUT':  65.0,
}

PAC_CONF = {
    'SMTP_SERVER': 'some-smtp-server.cac.washington.edu',
    'EMAIL_HEADERS': 'tests/templates/email_headers',
    'EMAIL_PLAIN': 'tests/templates/email_plain',
    'EMAIL_HTML': 'tests/templates/email_html',
    'EMAIL_PAC': True,
    'IDENTITY_URL': 'https://some-identity.s.uw.edu/new/accept',
}

# augment handlers' configs
for conf in (GWS_CONF, IRWS_CONF):
    if 'RUN_MODE' not in conf:
        conf['RUN_MODE'] = RUN_MODE
    if 'CERT_FILE' not in conf:
        conf['CERT_FILE'] = DEFAULT_CERT_FILE
    if 'KEY_FILE' not in conf:
        conf['KEY_FILE'] = DEFAULT_KEY_FILE
    if 'CA_FILE' not in conf:
        conf['CA_FILE'] = DEFAULT_CA_FILE

AWS_CONF = {
    'SNS_HOST':  'mock.xxx-1.amazonaws.com',
    'SNS_ARN':  'mock.arn:aws:sns::999909864246:iam-gws-activity-dev',
    'SNS_KEYID': 'mock-keyid',
    'SNS_KEY':   'mock-key',
    'SQS_KEYID': 'mock-keyid',
    'SQS_KEY':   'mock-key',
    'SQS_QUEUE':  'gws-sync-12.fifo',
    'REGION': 'us-west-2',
    'DEFAULT_KEYID': 'mock-keyid',
    'DEFAULT_KEY':   'mock-key',
}

IAM_CONF = {
    'CERTS':  [
        {
            "ID": "test-iamsig1",
            "URL": "file:%s/certs/test-2048.crt" % settings_path,
            "KEYFILE": "%s/certs/test-2048.key" % settings_path
        }
    ],
    'CRYPTS': [
     {"ID": "test-iamcrypt1",
      "KEY": "YjZmNTM5ZTE3M2QzNGZjOWExOWZhNGRlNTEyNWI0NTgK"
      },
     {"ID": "test-iamcrypt2",
      "KEY": "MDYyMzVmMTQ0ZmIyNDBhOGFhMTM0M2M4YTZkZjZlYWI="
      }
     ],
    'CA_FILE': "../certs/test-ca.crt",
    'SENDER': 'messaging tester'
}

LOGGING = {
    'version': 1,
    'formatters': {
        'plain': {
            'format': '%(message)s'
        },
        'plaintime': {
            'format': '%(asctime)s: %(message)s'
        },
        'syslog': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'default': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'stream': 'ext://sys.stdout',
            'formatter': 'plain',
        },
        'syslog': {
            'class': 'logging.handlers.SysLogHandler',
            'level': 'DEBUG',
            'formatter': 'syslog',
            'facility': 'LOG_LOCAL7'
        },
        'runlog': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'level': 'DEBUG',
            'formatter': 'syslog',
            'filename': '/home/fox/work/irws-watcher/process.log',
            'when': 'midnight'
        },
        'audits': {
            'class': 'logging.handlers.WatchedFileHandler',
            'level': 'INFO',
            'formatter': 'plaintime',
            'filename': '/home/fox/work/irws-watcher/audit.log',
        },
    },
    'loggers': {
      'root': {
        'level': 'DEBUG',
        'handlers': ['runlog', 'default'],
      },
      'message': {
        'level': 'DEBUG',
        'handlers': ['runlog'],
      },
      'recon': {
        'level': 'WARN',
        'handlers': ['runlog'],
      },
      'verify': {
        'level': 'DEBUG',
        'handlers': ['runlog', 'default'],
      },
      'audit': {
        'level': 'DEBUG',
        'handlers': ['audits']
      },
    }
}
