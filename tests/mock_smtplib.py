# mock smtplib SMTP client

class SMTP():

    def __init__(self, conf):
        self._conf = conf

    def sendmail(self, fromaddr, recip, msg):
        self._from = fromaddr
        self._recip = recip
        self._msg = msg

    def was_init(self):
        return self._conf

    def was_sendmail(self):
        return (self._from, self._recip, self._msg)
        
