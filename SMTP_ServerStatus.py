from servicenow_alert import install_exception_hooks as _install_servicenow_exception_hooks
_install_servicenow_exception_hooks()

import smtplib
from email.mime.multipart import MIMEMultipart
import time
from GraphEmail import FROM_ADDRESS

fromaddr = FROM_ADDRESS
toaddr = ["Srija_Gatla@csx.com"]
msg = MIMEMultipart()
msg['From'] = fromaddr
msg['To'] = ', '.join(toaddr)
msg['Subject'] = 'Python SMTP - Exception'
server = smtplib.SMTP('smtp.csx.com', 25)
server.starttls()


def checkifsmtpfail():
    i = 0
    server = smtplib.SMTP('smtp.csx.com', 25)
    server.starttls()
    status = server.noop()[0]
    while i < 3:
        print(status)
        if i < 3 and status != 250:
            # print('status---', status)
            time.sleep(5)
            print('waited 5 seconds')
            print(i)
            #server.sendmail(fromaddr, toaddr, msg.as_string())
            i += 1
            status = server.noop()[0]
            if status == 250:
                print('Success within 3 times')
                break
            else:
                continue
        else:

            # server.sendmail(fromaddr, toaddr, msg.as_string())
            # server.quit()
            if i > 3:
                print('SMTP server failed continuously for the 4th time')
            else:
                print('SMTP server connected at the first attempt')
                break





