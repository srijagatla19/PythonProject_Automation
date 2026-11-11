# -*- coding: utf-8 -*-
"""
Created on Fri Jul 16 18:42:37 2021

@author: z_edwemp_uat
"""
from servicenow_alert import install_exception_hooks as _install_servicenow_exception_hooks
_install_servicenow_exception_hooks()



import os
from email.encoders import encode_base64
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
import calendar
import datetime
import shutil
import time
import traceback
import sys
from GraphEmail import FROM_ADDRESS, send_graph_email
from servicenow_alert import create_failure_alert

today_ts = datetime.datetime.now()
today = datetime.datetime.now().date()
timestamp = datetime.datetime.strftime(today_ts,"%H-%M-%S")
currentMonth = calendar.month_abbr[today_ts.month]
currentMonth = calendar.month_name[list(calendar.month_abbr).index(currentMonth)]
currentDay = str(today_ts.day)
currentYear = str(today_ts.year)

def servicenow_send_alert(message, description, details):
    return create_failure_alert(
        message, description, details
    )


def attachEmailContent():
    with open(email, "r") as myfile:
        # data="".join(line.rstrip() for line in myfile)
        data = "".join(myfile)


# pdf = "//TJAX2008FS/Entshare/Performance Measurements/Executive Morning Package/EMP Support/ExecutePython/testing/dailyfiles/00 Cover Page - Executive Morning Package December 12, 2017.pdf"
# ehh_pdf = "//TJAX2008FS/Entshare/Performance Measurements/Executive Morning Package/EMP Support/EHH/Executive Morning Package - Streamlined - " + currentMonth +" "+ currentDay + ", " + currentYear + ".pdf"
# rev_pdf = "//TJAX2008FS/Entshare/Performance Measurements/Executive Morning Package/EMP Support/Revenue Secure/Executive Morning Package - Revenue - " + currentMonth +" "+ currentDay + ", " + currentYear + ".pdf"
# nonrev_pdf = "//TJAX2008FS/Entshare/Performance Measurements/Executive Morning Package/EMP Support/Non-Revenue/Executive Morning Package - Non-Revenue - " + currentMonth +" "+ currentDay + ", " + currentYear + ".pdf"

# ehh_pdf = "//TJAX2008FS/Entshare/Performance Measurements/Executive Morning Package/EMP Support/EHH/Executive Morning Package - Revenue Core - " + currentMonth +" "+ currentDay + ", " + currentYear + ".pdf"
rev_pdf = "//TJAX2008FS/Entshare/Performance Measurements/Executive Morning Package/EMP Support/Revenue Secure/Executive Morning Package - Revenue Core - " + currentMonth + " " + currentDay + ", " + currentYear + ".pdf"
nonrev_pdf = "//TJAX2008FS/Entshare/Performance Measurements/Executive Morning Package/EMP Support/Non-Revenue/Executive Morning Package - Non-Revenue Core - " + currentMonth + " " + currentDay + ", " + currentYear + ".pdf"
files_dir = "//TJAX2008FS/Entshare/Performance Measurements/Executive Morning Package/EMP Support/Daily Files"  # all the morning reports are here
terminal_pdf = "//TJAX2008FS/Entshare/Performance Measurements/Executive Morning Package/EMP Support/TerminalScorecard/Executive Morning Package - Terminal Scorecard - " + currentMonth + " " + currentDay + ", " + currentYear + ".pdf"
empdefinitions_pdf = "//TJAX2008FS/Entshare/Performance Measurements/Executive Morning Package/EMP Support/EMPDefintions/Executive Morning Package - EMP Definitions - " + currentMonth + " " + currentDay + ", " + currentYear + ".pdf"
regional_Scorecard_pdf = "//TJAX2008FS/Entshare/Performance Measurements/Executive Morning Package/EMP Support/RegionalScorecards/Regional Scorecards - " + currentMonth + " " + currentDay + ", " + currentYear + ".pdf"

email = "//TJAX2008FS/Entshare/Performance Measurements/Executive Morning Package/EMP Support/ExecutePython/EmailNotes.txt"
email_dir = "//TJAX2008FS/Entshare/Performance Measurements/Executive Morning Package/EMP Support/ExecutePython"
email_name = "EmailNotes.txt"
backup_dir = "//TJAX2008FS/Entshare/Performance Measurements/Executive Morning Package/EMP Support/ExecutePython/testing/email"
backup_name = "email.txt"

email_ehh = "//TJAX2008FS/Entshare/Performance Measurements/Executive Morning Package/EMP Support/ExecutePython/EHH_EmailNotes.txt"
email_rev = "//TJAX2008FS/Entshare/Performance Measurements/Executive Morning Package/EMP Support/ExecutePython/Rev_EmailNotes.txt"
email_nonrev = "//TJAX2008FS/Entshare/Performance Measurements/Executive Morning Package/EMP Support/ExecutePython/NonRev_EmailNotes.txt"

terminal_scorecard = "Executive Morning Package - Terminal Scorecard - " + currentMonth + " " + currentDay + ", " + currentYear + ".pdf"
emp_definitions = "Executive Morning Package - EMP Definitions - " + currentMonth + " " + currentDay + ", " + currentYear + ".pdf"
regional_scorecard = "Executive Morning Package - Regional Scorecard - " + currentMonth + " " + currentDay + ", " + currentYear + ".pdf"

fromaddr = FROM_ADDRESS
###########################################
# Correct DL's
# nonrev_bcc = ['DLPerformanceMeasurements@csx.com','Morrison_Waye@csx.com','Luma_Vasiljevic@csx.com','Rahul_Rai@csx.com','Tatini_Gandham@csx.com','Srija_Gatla@csx.com' ]
# rev_bcc = ['DLPerformanceMeasurements@csx.com','Morrison_Waye@csx.com','Luma_Vasiljevic@csx.com','Rahul_Rai@csx.com','Tatini_Gandham@csx.com','Srija_Gatla@csx.com' ]

# nonrev_toaddr = ['ExecutiveMorningPackage@csx.com']
nonrev_toaddr = ['Srija_Gatla@csx.com']
# rev_toaddr = ['DLExecutiveMorningPackageRevenue@csx.com']
rev_toaddr = ['Srija_Gatla@csx.com']

# sys_toaddr = ['Scheduling@csx.com']
sys_toaddr = ['Srija_Gatla@csx.com']
# sys_cc = ['Morrison_Waye@csx.com','BOADMINS@CSX.COM','EDWETL1@CSX.com','DLTechBusinessIntelligence@csx.com','BDA@csx.com','Srija_Gatla@csx.com' ]
sys_cc = ['Srija_Gatla@csx.com']

# toaddr_abort = [ 'EDWETL1@CSX.com']
toaddr_abort = ['Srija_Gatla@csx.com']
# cc_abort = ['EDWETL1@CSX.com','Srija_Gatla@csx.com' ]
cc_abort = ['Srija_Gatla@csx.com']

def sendRevenue():
    rev_subject_and_body = "Executive Morning Package - Revenue - " + currentMonth + " " + currentDay + ", " + currentYear
    revfilename = "Executive Morning Package - Revenue Core - " + currentMonth + " " + currentDay + ", " + currentYear + ".pdf"

    message = MIMEMultipart()
    message['Subject'] = rev_subject_and_body
    message['From'] = fromaddr
    message['To'] = ", ".join(rev_toaddr)

    with open(email_rev, "r") as email_revenue:
        # data="".join(line.rstrip() for line in myfile)
        revdata = "".join(email_revenue)

    ##attachEmailContent()

    text = MIMEText(rev_subject_and_body + "\n\n" + revdata)
    message.attach(text)

    with open(rev_pdf, "rb") as opened:
        openedfile = opened.read()
    attachedfile = MIMEApplication(openedfile, _subtype="pdf", _encoder=encode_base64)
    attachedfile.add_header('content-disposition', 'attachment', filename=revfilename)
    message.attach(attachedfile)

    with open(terminal_pdf, "rb") as opened:
        openedfile = opened.read()
    attachedfile = MIMEApplication(openedfile, _subtype="pdf", _encoder=encode_base64)
    attachedfile.add_header('content-disposition', 'attachment', filename=terminal_scorecard)
    message.attach(attachedfile)

    with open(regional_Scorecard_pdf, "rb") as opened:
        openedfile = opened.read()
    attachedfile = MIMEApplication(openedfile, _subtype="pdf", _encoder=encode_base64)
    attachedfile.add_header('content-disposition', 'attachment', filename=regional_scorecard)
    message.attach(attachedfile)

    with open(empdefinitions_pdf, "rb") as opened:
        openedfile = opened.read()
    attachedfile = MIMEApplication(openedfile, _subtype="pdf", _encoder=encode_base64)
    attachedfile.add_header('content-disposition', 'attachment', filename=emp_definitions)
    message.attach(attachedfile)

    send_graph_email(message, rev_toaddr + rev_bcc)

########## Non-Revenue##########################
def sendNonRevenue():
    nonrev_subject_and_body = "Executive Morning Package - Non-Revenue - " + currentMonth + " " + currentDay + ", " + currentYear
    nonrev_filename = "Executive Morning Package - Non-Revenue Core - " + currentMonth + " " + currentDay + ", " + currentYear + ".pdf"

    message = MIMEMultipart()
    message['Subject'] = nonrev_subject_and_body
    message['From'] = fromaddr
    message['To'] = ", ".join(nonrev_toaddr)
    ##message['Cc'] = ", ".join(nonrev_cc)

    with open(email_nonrev, "r") as email_nonrevenue:
        nonrevdata = "".join(email_nonrevenue)

    ##attachEmailContent()

    text = MIMEText(nonrev_subject_and_body + "\n\n" + nonrevdata)
    message.attach(text)

    with open(nonrev_pdf, "rb") as opened:
        openedfile = opened.read()
    attachedfile = MIMEApplication(openedfile, _subtype="pdf", _encoder=encode_base64)
    attachedfile.add_header('content-disposition', 'attachment', filename=nonrev_filename)
    message.attach(attachedfile)

    with open(terminal_pdf, "rb") as opened:
        openedfile = opened.read()
    attachedfile = MIMEApplication(openedfile, _subtype="pdf", _encoder=encode_base64)
    attachedfile.add_header('content-disposition', 'attachment', filename=terminal_scorecard)
    message.attach(attachedfile)

    with open(regional_Scorecard_pdf, "rb") as opened:
        openedfile = opened.read()
    attachedfile = MIMEApplication(openedfile, _subtype="pdf", _encoder=encode_base64)
    attachedfile.add_header('content-disposition', 'attachment', filename=regional_scorecard)
    message.attach(attachedfile)

    with open(empdefinitions_pdf, "rb") as opened:
        openedfile = opened.read()
    attachedfile = MIMEApplication(openedfile, _subtype="pdf", _encoder=encode_base64)
    attachedfile.add_header('content-disposition', 'attachment', filename=emp_definitions)
    message.attach(attachedfile)

    send_graph_email(message, nonrev_toaddr + nonrev_bcc)

########## Systems Management ##########################
def sendSuccessEmail():
    time.sleep(20)
    sys_subject_and_body = "Executive Morning Package Successfully Sent to the Senior Team - " + currentMonth + " " + currentDay + ", " + currentYear

    message = MIMEMultipart()
    message['Subject'] = sys_subject_and_body
    message['From'] = fromaddr
    message['To'] = ", ".join(sys_toaddr)
    message['Cc'] = ", ".join(sys_cc)

    text = MIMEText(sys_subject_and_body)
    message.attach(text)

    send_graph_email(message, sys_toaddr + sys_cc)
    
################### ABORT EMAIL TO EXECUTIVES ##################
def abort_process(automation_trigger, message):    
    #Copy the file to archive folder, append date to name of file, and timestamp within file. 
    archive_abort_filename = "EMP_Automation_" + str(today) + "_" + str(timestamp) + ".txt"
    shutil.copy(os.path.join(abort_path,abort_filename),os.path.join(abort_archive_path, archive_abort_filename))
    file = open((os.path.join(abort_archive_path, archive_abort_filename)), "a")
    file.write("\ntimestamp - " + str(today_ts))
    file.close()

    #Send email to notify users that automation has been turned off
    msg1 = MIMEMultipart()
    msg1['From'] = fromaddr
    msg1['To'] = ", ".join(toaddr_abort)
    msg1['Cc'] = ", ".join(cc_abort)
    msg1['Subject'] = message
    
    if 'OFF' in automation_trigger:
        txt = "Automation.txt file is set to OFF (X:/Performance Measurements/Executive Morning Package/EMP Support/ExecutePython/Automation.txt). "
    else:
        txt = 'Please review open ServiceNow incidents. '
        
    body1 = message + '\n' 
    body1 =  body1 + txt + '\n' 
    body1 = body1 + "EMP has NOT been sent to Executives." + '\n' 
    msg1.attach(MIMEText(body1, 'plain'))
    text1 = msg1.as_string()
    send_graph_email(msg1, toaddr_abort + cc_abort)
    
    #Change the text to ON within the Automation text file in ExecutePython Folder for tomorrow's automation to run.
    #file = open((os.path.join(abort_path, abort_filename)), "w")
    #file.write("ON")
    #file.close()
    
#    inn = open(os.path.join(abort_path, abort_filename)).read()
#    replacements = {'EMP': 'ON', 'PSR': 'ON'}
#    for i in replacements.keys():
#        inn = inn.replace(abort_dictionary[i], replacements[i])
#    file = open((os.path.join(abort_path, abort_filename)), "w")
#    file.write(inn)
#    file.close()
    
try:    
    # openAlerts = api.count_alerts()
    # countAlerts= openAlerts.data.count
    countAlerts=0
    print(countAlerts)
    
    #check if Automation is ON/OFF
    abort_path = "//TJAX2008FS/Entshare/Performance Measurements/Executive Morning Package/EMP Support/ExecutePython"
    abort_archive_path = "//TJAX2008FS/Entshare/Performance Measurements/Executive Morning Package/EMP Support/ExecutePython/archive"
    abort_filename = "Automation.txt"  ##File is updated by user when automation needs to be turned off. 
    
    #Read file to determine whether to send email to executives or to abort. Convert to Uppercase by default. 
    #file = open((os.path.join(abort_path, abort_filename)), "r")
    #automation_trigger = file.read().upper()
    #file.close()
    
    with open((os.path.join(abort_path, abort_filename))) as f:
        abort_dictionary = dict(x.rstrip().split(None, 1) for x in f)
    f.close()
    automation_trigger = abort_dictionary.get('EMP').upper()
    
    
    if countAlerts == 0 and automation_trigger == "ON":
        sendRevenue()
        sendNonRevenue()
        sendSuccessEmail()
        
    elif countAlerts !=0 and automation_trigger == "ON":
        message = "EMP - There are open ServiceNow incidents."
        abort_process(automation_trigger, message)
        
        servicenow_details = {}
        servicenow_message = 'EMP High Alert - EMP has not been sent to DL'
        servicenow_description = "An open ServiceNow incident prior to 5 A.M. caused EMP to not be sent to Executives."
        servicenow_send_alert(servicenow_message, servicenow_description, servicenow_details)
        
    elif automation_trigger != "ON":
        message = "EMP Automation is turned OFF."
        abort_process(automation_trigger, message)
        
        servicenow_details = {}
        servicenow_message = 'EMP High Alert - EMP has not been sent to DL'
        servicenow_description = "Automation.txt file is set to EMP OFF (X:/Performance Measurements/Executive Morning Package/EMP Support/ExecutePython/Automation.txt)"
        servicenow_send_alert(servicenow_message, servicenow_description, servicenow_details)
        
except Exception as e:
    servicenow_details = {}
    servicenow_details['File Name'] = os.path.basename(sys.argv[0])
    print(e)
    print(traceback.print_exc())
    servicenow_message = 'EMP - Python Coding Error'
    servicenow_description = str(e) + '\n\n'
    servicenow_description = servicenow_description + traceback.format_exc()
    servicenow_send_alert(servicenow_message, servicenow_description, servicenow_details)

exit()
