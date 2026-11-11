# -*- coding: utf-8 -*-
"""
Created on Thu Jan 04 17:30:10 2018

@author: z_edwemp_uat
"""
from servicenow_alert import install_exception_hooks as _install_servicenow_exception_hooks
_install_servicenow_exception_hooks()


import os
from email.encoders import encode_base64
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
# from email.mime.base import MIMEBase
from email.mime.text import MIMEText
import calendar
import datetime
import shutil
import time
# from datetime import timedelta
import traceback
from servicenow_alert import create_failure_alert
import sys
from PyPDF2 import PdfReader
from AutomationLog import log_step
from GraphEmail import FROM_ADDRESS, send_graph_email


log_step("Email", "START: executive email workflow")

today_ts = datetime.datetime.now()
today = datetime.datetime.now().date()
currentMonth = calendar.month_abbr[today_ts.month]
currentMonth=calendar.month_name [list(calendar.month_abbr).index(currentMonth)]
currentDay = str(today_ts.day)
currentYear = str(today_ts.year)
today_string = today.strftime('%Y-%m-%d')
timestamp = datetime.datetime.strftime(today_ts,"%H-%M-%S")

def servicenow_send_alert(message, description, details):
    return create_failure_alert(
        message, description, details
    )


def attachEmailContent():
    with open (email, "r") as myfile:
    #data="".join(line.rstrip() for line in myfile)
        data = "".join(myfile)

#pdf = "//TJAX2008FS/Entshare/Performance Measurements/Executive Morning Package/EMP Support/ExecutePython/testing/dailyfiles/00 Cover Page - Executive Morning Package December 12, 2017.pdf"
#ehh_pdf = "//TJAX2008FS/Entshare/Performance Measurements/Executive Morning Package/EMP Support/EHH/Executive Morning Package - Streamlined - " + currentMonth +" "+ currentDay + ", " + currentYear + ".pdf"
#rev_pdf = "//TJAX2008FS/Entshare/Performance Measurements/Executive Morning Package/EMP Support/Revenue Secure/Executive Morning Package - Revenue - " + currentMonth +" "+ currentDay + ", " + currentYear + ".pdf"
#nonrev_pdf = "//TJAX2008FS/Entshare/Performance Measurements/Executive Morning Package/EMP Support/Non-Revenue/Executive Morning Package - Non-Revenue - " + currentMonth +" "+ currentDay + ", " + currentYear + ".pdf"

#ehh_pdf = "//TJAX2008FS/Entshare/Performance Measurements/Executive Morning Package/EMP Support/EHH/Executive Morning Package - Revenue Core - " + currentMonth +" "+ currentDay + ", " + currentYear + ".pdf"
rev_pdf = "//TJAX2008FS/Entshare/Performance Measurements/Executive Morning Package/EMP Support/Revenue Secure/Executive Morning Package - Revenue Core - " + currentMonth +" "+ currentDay + ", " + currentYear + ".pdf"
nonrev_pdf = "//TJAX2008FS/Entshare/Performance Measurements/Executive Morning Package/EMP Support/Non-Revenue/Executive Morning Package - Non-Revenue Core - " + currentMonth +" "+ currentDay + ", " + currentYear + ".pdf"
files_dir = "//TJAX2008FS/Entshare/Performance Measurements/Executive Morning Package/EMP Support/Daily Files" #all the morning reports are here
terminal_pdf = "//TJAX2008FS/Entshare/Performance Measurements/Executive Morning Package/EMP Support/TerminalScorecard/Executive Morning Package - Terminal Scorecard - " + currentMonth +" "+ currentDay + ", " + currentYear + ".pdf"
empdefinitions_pdf = "//TJAX2008FS/Entshare/Performance Measurements/Executive Morning Package/EMP Support/EMPDefintions/Executive Morning Package - EMP Definitions - " + currentMonth +" "+ currentDay + ", " + currentYear + ".pdf"
regional_Scorecard_pdf = "//TJAX2008FS/Entshare/Performance Measurements/Executive Morning Package/EMP Support/RegionalScorecards/Regional Scorecards - " + currentMonth + " " + currentDay + ", " + currentYear +  ".pdf"


email = "//TJAX2008FS/Entshare/Performance Measurements/Executive Morning Package/EMP Support/ExecutePython/EmailNotes.txt"
email_name = "EmailNotes.txt"
backup_dir = "//TJAX2008FS/Entshare/Performance Measurements/Executive Morning Package/EMP Support/ExecutePython/testing/email"
backup_name = "email.txt"

email_dir = "//TJAX2008FS/Entshare/Performance Measurements/Executive Morning Package/EMP Support/ExecutePython"
email_ehh = "//TJAX2008FS/Entshare/Performance Measurements/Executive Morning Package/EMP Support/ExecutePython/EHH_EmailNotes.txt"
email_rev = "//TJAX2008FS/Entshare/Performance Measurements/Executive Morning Package/EMP Support/ExecutePython/Rev_EmailNotes.txt"
email_nonrev =  "//TJAX2008FS/Entshare/Performance Measurements/Executive Morning Package/EMP Support/ExecutePython/NonRev_EmailNotes.txt"
emailarchive_path = "//TJAX2008FS/Entshare/Performance Measurements/Executive Morning Package/EMP Support/ExecutePython/archive"
email_regional =  "//TJAX2008FS/Entshare/Performance Measurements/Executive Morning Package/EMP Support/ExecutePython/Regional_EmailNotes.txt"

terminal_scorecard = "Executive Morning Package - Terminal Scorecard - " + currentMonth +" "+ currentDay + ", " + currentYear + ".pdf"
emp_definitions = "Executive Morning Package - EMP Definitions - " + currentMonth +" "+ currentDay + ", " + currentYear + ".pdf"
regional_scorecard = "Regional Scorecards - " + currentMonth + " " + currentDay + ", " + currentYear + ".pdf"


fromaddr = FROM_ADDRESS


sys_toaddr = ['Scheduling@csx.com']
# sys_toaddr = ['Srija_Gatla@csx.com']
sys_cc = [ 'Morrison_Waye@csx.com','BOADMINS@CSX.COM','EDWETL1@CSX.com','DLTechBusinessIntelligence@csx.com','BDA@csx.com','Srija_Gatla@csx.com' ,'Sunkara_ChandanaSudha@csx.com']
# sys_cc = ['Srija_Gatla@csx.com']

#Interim DL's
nonrev_toaddr = ['DLPerformanceMeasurements@csx.com','Michael_Cheatham@csx.com','Morrison_Waye@csx.com','Luma_Vasiljevic@csx.com','Rahul_Rai@csx.com','BOADMINS@CSX.COM','EDWETL1@CSX.com','DLTechBusinessIntelligence@csx.com']
# nonrev_toaddr = ['Srija_Gatla@csx.com']
rev_toaddr = ['DLPerformanceMeasurements@csx.com','Michael_Cheatham@csx.com','Morrison_Waye@csx.com']
# rev_toaddr = ['Srija_Gatla@csx.com']
# nonrev_bcc =['Srija_Gatla@csx.com']
# rev_bcc =['Srija_Gatla@csx.com']

nonrev_bcc =['Tatini_Gandham@csx.com','Srija_Gatla@csx.com','Sunkara_ChandanaSudha@csx.com']
rev_bcc = ['Luma_Vasiljevic@csx.com','Rahul_Rai@csx.com','Tatini_Gandham@csx.com','Srija_Gatla@csx.com','Sunkara_ChandanaSudha@csx.com']

def attach_pdf(message, pdf_path, attachment_name):
    log_step("Email", f"START: attach PDF {pdf_path}")
    with open(pdf_path, "rb") as opened:
        opened_file = opened.read()
    attached_file = MIMEApplication(
        opened_file, _subtype="pdf", _encoder=encode_base64
    )
    attached_file.add_header(
        "content-disposition", "attachment", filename=attachment_name
    )
    message.attach(attached_file)
    log_step(
        "Email",
        f"END: attached {attachment_name}; bytes={len(opened_file)}",
    )


def archiveEmailNotes():
    
    if os.path.getsize(os.path.join(email_dir, email_regional)) > 0:
        archive_filename = "Regional_EmailNotes" + str(today) + "_" + str(timestamp) + ".txt"
        shutil.copy(os.path.join(email_dir,email_regional),os.path.join(emailarchive_path, archive_filename))
        
    if os.path.getsize(os.path.join(email_dir, email_rev)) > 0:
        archive_filename = "Rev_EmailNotes" + str(today) + "_" + str(timestamp) + ".txt"
        shutil.copy(os.path.join(email_dir,email_rev),os.path.join(emailarchive_path, archive_filename))
        #file = open((os.path.join(email_dir, email_rev)), "w")
        #file.write("")
        #file.close()
    if os.path.getsize(os.path.join(email_dir, email_nonrev)) > 0:
        archive_filename = "NonRev_EmailNotes" + str(today) + "_" + str(timestamp) + ".txt"
        shutil.copy(os.path.join(email_dir,email_nonrev),os.path.join(emailarchive_path, archive_filename))
        #file = open((os.path.join(email_dir, email_nonrev)), "w")
        #file.write("")
        #file.close()

try:       
    required_attachments = (
        (rev_pdf, "Revenue Core"),
        (nonrev_pdf, "Non-Revenue Core"),
        (terminal_pdf, "Terminal Scorecard"),
        (regional_Scorecard_pdf, "Regional Scorecards"),
        (empdefinitions_pdf, "EMP Definitions"),
    )
    missing_attachments = []
    for attachment_path, description in required_attachments:
        log_step("Email", f"START: verify {description} PDF {attachment_path}")
        if not os.path.isfile(attachment_path):
            missing_attachments.append(f"{description}: {attachment_path}")
            log_step("Email", f"ERROR: missing {description} PDF {attachment_path}")
        else:
            with open(attachment_path, "rb") as attachment_file:
                page_count = len(PdfReader(attachment_file, strict=True).pages)
            if not page_count:
                raise ValueError(f"{description} PDF contains no pages: {attachment_path}")
            log_step(
                "Email",
                f"END: verified {description} PDF; pages={page_count}",
            )
    if missing_attachments:
        raise FileNotFoundError(
            "Required email attachment(s) are missing; no business email sent:\n"
            + "\n".join(missing_attachments)
        )

    ########## Revenue ################
    log_step("Email", "START: prepare Revenue email")
    rev_subject_and_body = "Executive Morning Package - Revenue - " + currentMonth + " " + currentDay + ", " + currentYear
    revfilename = "Executive Morning Package - Revenue Core - " + currentMonth +" "+ currentDay + ", " + currentYear + ".pdf"
    
    message = MIMEMultipart()
    message['Subject'] = rev_subject_and_body
    message['From'] = fromaddr
    message['To'] = ", ".join(rev_toaddr)
    
    
    with open (email_rev, "r") as email_revenue:
        #data="".join(line.rstrip() for line in myfile)
        revdata = "".join(email_revenue)
     
        
    ##attachEmailContent()
    
    text = MIMEText(rev_subject_and_body + "\n\n" + revdata)
    message.attach(text)
    
    attach_pdf(message, rev_pdf, revfilename)
    attach_pdf(message, terminal_pdf, terminal_scorecard)
    attach_pdf(message, regional_Scorecard_pdf, regional_scorecard)
    attach_pdf(message, empdefinitions_pdf, emp_definitions)
    
    log_step("Email", "START: send Revenue email through Microsoft Graph")
    send_graph_email(message, rev_toaddr + rev_bcc)
    log_step("Email", "END: Revenue email sent")
    
    with open("//TJAX2008FS/Entshare/Performance Measurements/Executive Morning Package/EMP Support/ExecutePython/logs/RevenueSentSuccess.txt",
              "a") as text_file:
        text_file.write("Revenue email sent. " + str(today_ts) + "\n")
                
    
    ########## Non-Revenue##########################
    log_step("Email", "START: prepare Non-Revenue email")
    nonrev_subject_and_body = "Executive Morning Package - Non-Revenue - " + currentMonth +" "+ currentDay + ", " + currentYear
    nonrev_filename = "Executive Morning Package - Non-Revenue Core - " + currentMonth +" "+ currentDay + ", " + currentYear + ".pdf"
    
    message = MIMEMultipart()
    message['Subject'] = nonrev_subject_and_body
    message['From'] = fromaddr
    message['To'] = ", ".join(nonrev_toaddr)
    ##message['Cc'] = ", ".join(nonrev_cc)
    
    with open (email_nonrev, "r") as email_nonrevenue:
        nonrevdata = "".join(email_nonrevenue)
        
    ##attachEmailContent()
    
    text = MIMEText(nonrev_subject_and_body + "\n\n" + nonrevdata)
    message.attach(text)
    
    attach_pdf(message, nonrev_pdf, nonrev_filename)
    attach_pdf(message, terminal_pdf, terminal_scorecard)
    attach_pdf(message, regional_Scorecard_pdf, regional_scorecard)
    attach_pdf(message, empdefinitions_pdf, emp_definitions)
    
    log_step("Email", "START: send Non-Revenue email through Microsoft Graph")
    send_graph_email(message, nonrev_toaddr + nonrev_bcc)
    log_step("Email", "END: Non-Revenue email sent")
    
    with open("//TJAX2008FS/Entshare/Performance Measurements/Executive Morning Package/EMP Support/ExecutePython/logs/NonRevSentSuccess.txt",
              "a") as text_file:
        text_file.write("NonRevenue email sent. " + str(today_ts) + "\n")
    
    ########## Systems Management ##########################
    log_step("Email", "START: internal notification; wait 20 seconds")
    time.sleep(20)
    sys_subject_and_body = "Executive Morning Package Successfully Sent to Internal Team- - " + currentMonth +" "+ currentDay + ", " + currentYear
    
    message = MIMEMultipart()
    message['Subject'] = sys_subject_and_body
    message['From'] = fromaddr
    message['To'] = ", ".join(sys_toaddr)
    message['Cc'] = ", ".join(sys_cc)
        
    text = MIMEText(sys_subject_and_body)
    message.attach(text)
    
    log_step("Email", "START: send internal notification through Microsoft Graph")
    send_graph_email(message, sys_toaddr + sys_cc)
    log_step("Email", "END: internal notification sent")
    
    #############################################################################
    
    ##filelist = [ f for f in os.listdir(files_dir) if f.endswith(".pdf") ]
    ##for f in filelist:
    ##    os.remove(os.path.join(files_dir, f))
    
    #shutil.copy(os.path.join(email_dir, email_name),os.path.join(backup_dir, backup_name))
    #open(email, 'w').close()
    
    #Archive Cover Page for next days run
    cover_path = "//TJAX2008FS/Entshare/Performance Measurements/Executive Morning Package/EMP Support/Daily Files"
    archive_path = "//TJAX2008FS/Entshare/Performance Measurements/Executive Morning Package/EMP Support/Daily Files/Archive"
    pdf = [f for f in os.listdir(cover_path) if f.endswith("pdf") and "00" in f]
    cover_name = ''.join(pdf)
    
    if pdf:
        log_step("Email", f"START: archive cover PDF {cover_name}")
        shutil.move(os.path.join(cover_path, cover_name),os.path.join(archive_path, cover_name))
        log_step("Email", f"END: archived cover PDF {cover_name}")
    
    log_step("Email", "START: archive email notes")
    archiveEmailNotes()
    log_step("Email", "END: archive email notes")
    log_step("Email", "END: executive email workflow")

except Exception as e:
    log_step("Email", f"ERROR: {type(e).__name__}: {e}\n{traceback.format_exc()}")
    servicenow_details = {}
    servicenow_details['File Name'] = os.path.basename(sys.argv[0])
    print(e)
    print(traceback.print_exc())
    servicenow_message = 'EMP - Python Coding Error'
    servicenow_description = str(e) + '\n\n'
    servicenow_description = servicenow_description + traceback.format_exc()
    servicenow_send_alert(servicenow_message, servicenow_description, servicenow_details)
    raise
