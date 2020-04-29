# mock smtplib SMTP client

conf = None
num_calls = 0
m_from = []
m_recip = []
m_msg = []


class SMTP():

    def __init__(self, conf=None):
        conf = conf

    def sendmail(self, fromaddr, recip, msg):
        global num_calls
        m_from.append(fromaddr)
        m_recip.append(recip)
        m_msg.append(msg)
        num_calls += 1

    def usage(self):
        return (num_calls, m_from, m_recip, m_msg)
