# -*- coding: utf-8 -*-
"""
Created on Fri Jan 31 11:51:43 2020

@author: z_edwemp_uat
"""
from servicenow_alert import install_exception_hooks as _install_servicenow_exception_hooks
_install_servicenow_exception_hooks()


# from reportlab.pdfgen.canvas import Canvas
import os, time
from io import BytesIO
from PyPDF2 import PdfWriter, PdfReader
import datetime
from datetime import timedelta
import calendar
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.encoders import encode_base64
import shutil
import traceback
from servicenow_alert import create_failure_alert
import sys
from AutomationLog import log_step
from GraphEmail import FROM_ADDRESS, send_graph_email


log_step("CoverPage", "START: cover-page automation")

today_ts = datetime.datetime.now()
today = datetime.datetime.now().date()
currentMonth = calendar.month_abbr[today_ts.month]
currentMonth = calendar.month_name[list(calendar.month_abbr).index(currentMonth)]
currentDay = str(today_ts.day)
currentMon_Day = currentMonth + " " + currentDay
currentYear = str(today_ts.year)
yesterday = today - timedelta(1)
yesterdayMonth = calendar.month_abbr[yesterday.month]
yesterdayMonth = calendar.month_name[list(calendar.month_abbr).index(yesterdayMonth)]
yesterdayDay = str(yesterday.day)
yesterdayYear = str(yesterday.year)


def servicenow_send_alert(message, description, details):
    return create_failure_alert(
        message, description, details
    )


def getSize(filename):
    st = os.stat(filename)
    return st.st_size


def sendEmail(coverName):
    log_step("CoverPage", f"START: prepare email with attachment {coverName}")
    subject_and_body = "Safety Report - " + currentMonth + " " + currentDay + ", " + currentYear
    fromaddr = FROM_ADDRESS
    toaddr = ['Steve_Swanson@CSX.com','Greg_Barney@csx.com','Shawn_Shanahan@csx.com','Edward_Cox@csx.com']
    # toaddr = ['Srija_Gatla@csx.com']
    tocc = ['Morrison_Waye@csx.com','Suman_Katragadda@csx.com','Tatini_Gandham@csx.com','Srija_Gatla@csx.com','Sunkara_ChandanaSudha@csx.com']
    # tocc = ['Srija_Gatla@csx.com']
    

    message = MIMEMultipart()
    message['Subject'] = subject_and_body
    message['From'] = fromaddr
    message['To'] = ", ".join(toaddr)
    message['Cc'] = ", ".join(tocc)

    ##attachEmailContent()

    text = MIMEText(subject_and_body + "\n\n")
    message.attach(text)

    with open(path_to_watch + "/" + coverName, "rb") as opened:
        openedfile = opened.read()
    attachedfile = MIMEApplication(openedfile, _subtype="pdf", _encoder=encode_base64)
    attachedfile.add_header('content-disposition', 'attachment', filename=coverName)
    message.attach(attachedfile)

    log_step("CoverPage", "START: send safety report email through Microsoft Graph")
    send_graph_email(message, toaddr + tocc)
    log_step("CoverPage", "END: safety report email sent")


def sendEmailSuccess():
    log_step("CoverPage", "START: connect to SMTP for cover-page success email")
    # email setup
    fromaddr = FROM_ADDRESS
    toaddr = ['Morrison_Waye@csx.com']
    # toaddr = ['Srija_Gatla@csx.com']
    cc = ['EDWETL1@CSX.com','BDA@csx.com','BOADMINS@CSX.COM','DLTechBusinessIntelligence@csx.com','Srija_Gatla@csx.com','Sunkara_ChandanaSudha@csx.com']
    # cc = ['Srija_Gatla@csx.com']
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = ", ".join(toaddr)
    msg['Cc'] = ", ".join(cc)
    msg['Subject'] = "EMP Automation: Cover Page .pdf move successful."
    body = "Cover Page .pdf is copied to daily files folder from CoverPage_New folder"
    msg.attach(MIMEText(body, 'plain'))
    send_graph_email(msg, toaddr + cc)
    log_step("CoverPage", "END: cover-page success email sent")


def sendEmailFail():
    log_step("CoverPage", "START: send missing-safety-report notification")
    # email setup
    fromaddr = FROM_ADDRESS
    toaddr = ['Srija_Gatla@csx.com']
    cc = ['EDWETL1@CSX.com']
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = ", ".join(toaddr)
    msg['Cc'] = ", ".join(cc)
    msg['Subject'] = "EMP Cover Page Automation: Today's Safety Report not found "
    body = "Today's Safety Report is not found. \n\nPlease check the directory: //TJAX2008FS/Entshare/Performance Measurements/Executive Morning Package/EMP Support/Daily Files/CoverPage_New"
    msg.attach(MIMEText(body, 'plain'))
    send_graph_email(msg, toaddr + cc)
    log_step("CoverPage", "END: missing-safety-report notification sent")


# Added function to look for irrelevant 00 cover page pdf and delete at the beginning, changes done by Z8182 - 10/9/2023

def delete_00_coverpage():
    cover_dir = "//TJAX2008FS/Entshare/Performance Measurements/Executive Morning Package/EMP Support/Daily Files"
    log_step("CoverPage", f"START: scan for old cover PDFs in {cover_dir}")
    cover_pdf = [f for f in os.listdir(cover_dir) if f.startswith("00") and f.endswith(".pdf")]
    if cover_pdf:
        for i in cover_pdf:
            cover_path = os.path.join(cover_dir, i)
            log_step("CoverPage", f"START: delete old cover PDF {cover_path}")
            try:
                os.remove(cover_path)
            except OSError as error:
                log_step("CoverPage", f"ERROR: could not delete {cover_path}: {error}")
                raise
            log_step("CoverPage", f"END: deleted old cover PDF {cover_path}")
            # print(i)
    log_step("CoverPage", f"END: old-cover scan found {len(cover_pdf)} matching PDF(s)")
delete_00_coverpage()


def copyToDailyFiles(pdf_name):
    ##copy pdf to daily files folder
    log_step("CoverPage", f"START: copy cleaned report {pdf_name} to {dest_path}")
    shutil.copy(os.path.join(path_to_watch, pdf_name), os.path.join(dest_path, cover_name))
    log_step("CoverPage", f"END: copied report to {os.path.join(dest_path, cover_name)}")
    ##write CoverPageSuccess.txt to trigger folder
    with open(
            "//TJAX2008FS/Entshare/Performance Measurements/Executive Morning Package/EMP Support/ExecutePython/logs/CoverPageSuccess.txt",
            "a") as text_file:
        text_file.write("Cover Page is successfuly copied to Daily Files Folder. " + str(today_ts) + "\n")


def clean_safetyReport(pdf_name, path_to_watch):
    source_path = os.path.join(path_to_watch, pdf_name)
    log_step("CoverPage", f"START: clean safety report {source_path}")
    output = PdfWriter()
    tempoutput = PdfWriter()
    tempFinal = PdfWriter()

    log_step("CoverPage", f"START: open/read source PDF {source_path}")
    f = open(source_path, "rb")
    input1 = PdfReader(f)
    # input1 = PdfReader(open( path_to_watch + "/" + pdf_name, "rb"))
    # print (pdf_name + " has %d pages." % len(len(len(len(input1.pages)))))
    numPages1 = len(input1.pages)
    log_step("CoverPage", f"END: source PDF read; pages={numPages1}")

    for i in range(numPages1):
        log_step("CoverPage", f"START: inspect page {i + 1}/{numPages1}")
        page = input1.pages[i]
        tempoutput.add_page(page)
        outputStreamTemp = BytesIO()
        tempoutput.write(outputStreamTemp)

        page = input1.pages[i]
        pdfsize1 = len(outputStreamTemp.getvalue())
        if pdfsize1 < 6000:
            print("Page number " + str(i + 1) + " is blank.")

        elif pdfsize1 >= 6000:
            print("Page number " + str(i + 1) + " is not blank.")
            tempFinal.add_page(page)
        print(pdfsize1)

        tempoutput = PdfWriter()
        log_step("CoverPage", f"END: inspected page {i + 1}/{numPages1}")

    cleaned_path = os.path.join(path_to_watch, cover_Clean)
    log_step("CoverPage", f"START: write cleaned PDF {cleaned_path}")
    outputStreamTemp1 = open(cleaned_path, "wb")
    tempFinal.write(outputStreamTemp1)
    outputStreamTemp1.close()
    log_step("CoverPage", f"END: cleaned PDF written {cleaned_path}")
    sendEmail(cover_Clean)
    copyToDailyFiles(cover_Clean)
    log_step("CoverPage", "START: send cover-page success email")
    sendEmailSuccess()
    log_step("CoverPage", "END: cover-page success email sent")
    # os.remove(path_to_watch + "/" + cover_Clean)
    f.close()
    log_step("CoverPage", f"START: remove temporary cleaned PDF {cleaned_path}")
    os.remove(cleaned_path)
    log_step("CoverPage", "END: removed temporary cleaned PDF")
    # os.remove(os.path.join(path_to_watch, pdf_name))


try:
    log_step("CoverPage", "START: inspect report input folders")
    path_to_watch = "//TJAX2008FS/Entshare/Performance Measurements/Executive Morning Package/EMP Support/Daily Files/CoverPage_New"
    dest_path = "//TJAX2008FS/Entshare/Performance Measurements/Executive Morning Package/EMP Support/Daily Files"
    cover_name = "00 " + "Cover Page - Executive Morning Package " + " -" + currentMonth + " " + currentDay + ", " + currentYear + ".pdf"
    bobj_dir = "//TJAX6000FS/APPDEV/Data Warehouse Public/Business Objects/Morning Package"

    # cover_page = "Safety Report.pdf"
    cover_Clean = "Safety Report " + today.isoformat() + ".pdf"
    minutes = 0
    bobj_time = []
    pdf_name = ""

    bobj_files = [f for f in os.listdir(bobj_dir) if f.endswith("pdf")]
    log_step("CoverPage", f"END: found {len(bobj_files)} PDFs in report source folder")

    log_step("CoverPage", f"START: list cover input PDFs in {path_to_watch}")
    pdf = [
        f
        for f in os.listdir(path_to_watch)
        if f.endswith("pdf") and f != cover_Clean
    ]
    log_step("CoverPage", f"END: found {len(pdf)} PDFs in cover-page input folder")

    for f in pdf:
        log_step("CoverPage", f"START: evaluate cover-page input {f}")
        name = os.path.join(path_to_watch, f)
        try:
            file_time = os.path.getmtime(name)
        except FileNotFoundError:
            log_step(
                "CoverPage",
                f"WARNING: skip cover-page input that disappeared during scan: {name}",
            )
            continue
        file_time1 = datetime.date.fromtimestamp(file_time)
        if file_time1 >= yesterday and 'Safety Report' in name:
            pdf_name = ''.join(f)
            log_step("CoverPage", f"Selected current safety report {pdf_name} from cover-page folder")
            clean_safetyReport(pdf_name, path_to_watch)
        else:
            if f in bobj_files:
                bobj_name = os.path.join(bobj_dir, f)
                file_time = os.path.getmtime(bobj_name)
                file_time1 = datetime.date.fromtimestamp(file_time)
                if file_time1 >= yesterday:
                    pdf_name = ''.join(f)
                    path_to_watch = bobj_dir
                    log_step("CoverPage", f"Selected current safety report {pdf_name} from report source folder")
                    clean_safetyReport(pdf_name, path_to_watch)
                else:
                    sendEmailFail()
                    bobj_time.append(f)
            else:
                sendEmailFail()

    if not pdf:
        for f in bobj_files:
            bobj_name = os.path.join(bobj_dir, f)
            file_time = os.path.getmtime(bobj_name)
            file_time1 = datetime.date.fromtimestamp(file_time)
            if file_time1 >= yesterday and 'Safety Report' in f:
                pdf_name = ''.join(f)
                path_to_watch = bobj_dir
                clean_safetyReport(pdf_name, path_to_watch)
            elif file_time1 < yesterday and 'Safety Report' in name:
                sendEmailFail()
                bobj_time.append(f)

    ########################### FILE WATCHER BEGIN #########################################################################
    # Watch files till 5:15 AM for today's reports in bobj folder.
    # If the reports get updated with today's timestamp - use in merge process.
    # If not found after 5:15 - send email.

    time1 = datetime.datetime.strptime('05:15:00', '%H:%M:%S')
    time2 = datetime.datetime.strptime(datetime.datetime.strftime(today_ts, "%H:%M:%S"), '%H:%M:%S')
    tsdelta = max(0, (time1 - time2).total_seconds())
    tmdelta = tsdelta / 60
    log_step(
        "CoverPage",
        f"Watcher deadline is 05:15 local time; remaining_minutes={tmdelta:.1f}",
    )

    minutes = 0
    i = 0
    bobj_pdfs_merge = []

    if bobj_time:
        log_step("CoverPage", f"START: wait for {len(bobj_time)} report(s) to update")
        while i < len(bobj_time) and minutes < tmdelta:
            n0 = bobj_time[i]
            n = os.path.join(bobj_dir, n0)
            # print n
            t = os.path.getmtime(n)
            t1 = datetime.date.fromtimestamp(t)
            if t1 >= yesterday:  #
                # print bobj_time[i]
                # print "deleting this file in time list"
                del bobj_time[i]
                bobj_pdfs_merge.append(n0)
                path_to_watch = bobj_dir
                pdf_name = ''.join(n0)
                clean_safetyReport(pdf_name, path_to_watch)

            while minutes < tmdelta and t1 < yesterday:
                # print minutes
                log_step("CoverPage", f"WAIT: report {n0} is not current; next check in 60 seconds")
                time.sleep(60)
                minutes = minutes + 1
                n0 = bobj_time[i]
                n = os.path.join(bobj_dir, n0)
                t = os.path.getmtime(n)
                t1 = datetime.date.fromtimestamp(t)
                # print t1
                # print minutes
                if t1 >= yesterday:
                    # print "FOUND PDF - todays timestamp", bobj_time[i], t1
                    # print "deleting this file"
                    del bobj_time[i]
                    bobj_pdfs_merge.append(n0)
                    pdf_name = ''.join(n0)
                    path_to_watch = bobj_dir
                    clean_safetyReport(pdf_name, path_to_watch)
                    # print "files remaining after deleting", bobj_time
            i = i + 1

    if bobj_time:
        sendEmailFail()

    log_step("CoverPage", "START: import and run MergePdfs")
    import MergePdfs
    log_step("CoverPage", "END: MergePdfs import returned")
    import subprocess

    create = [sys.executable, 'MergePdfs.py']

except KeyboardInterrupt:
    log_step("CoverPage", "INTERRUPTED: automation stopped by user\n" + traceback.format_exc())
    raise
except Exception as e:
    log_step("CoverPage", f"ERROR: {type(e).__name__}: {e}\n{traceback.format_exc()}")
    servicenow_details = {}
    servicenow_details['File Name'] = os.path.basename(sys.argv[0])
    # print(e)
    traceback.print_exc()
    servicenow_message = 'EMP - Python Coding Error'
    servicenow_description = str(e) + '\n\n'
    servicenow_description = servicenow_description + traceback.format_exc()
    servicenow_send_alert(servicenow_message, servicenow_description, servicenow_details)
    raise

#################### FILE WATCHER  END #########################################################

# if not today_pdf:
#    before = dict([(f, None) for f in os.listdir(path_to_watch) if f.endswith("pdf")])
#    print before
#    after = dict([(f, None) for f in os.listdir(path_to_watch) if f.endswith("pdf")])
#    print after
#    while before==after and minutes < 120:
#            #after = dict([(f, None) for f in os.listdir(path_to_watch) if f.endswith("pdf")])
#            #print after
#            if after==before and minutes < 120:
#                print  minutes
#                print "im sleeping for 30 sec"
#                time.sleep(30)
#                minutes = minutes + 1
#                print  minutes
#                after = dict([(f, None) for f in os.listdir(path_to_watch) if f.endswith("pdf")])
#                print after
#            #if after==before and minutes >= 120:
#            if minutes >= 120:
#                sendEmailFail()
#            if before!= after:
#                #print "found pdf"
#                added = [f for f in after if not f in before]
#                pdf_name = ''.join(added)
#                clean_safetyReport(pdf_name, path_to_watch)
#                #copyToDailyFiles(pdf_name)
#                #sendEmailSuccess()


# =============================================================================
# if pdf_name:
#     input1 = PdfReader(open( path_to_watch + "/" + pdf_name, "rb"))
#     print (pdf_name + " has %d pages." % len(len(len(len(input1.pages))))())
#     numPages1=len(len(len(len(input1.pages))))()
# 
#     for i in range(numPages1):
#     
#         page=input1.pages[i]
#     
#         tempoutput.add_page(page)
#         outputStreamTemp = open("paginasize.pdf", "wb")
#         tempoutput.write(outputStreamTemp)
#     
#         page=input1.pages[i]
#         pdfsize1= getSize("paginasize.pdf")
#         if pdfsize1<6000:
#             print("Page number " + str(i+1) +" is blank.")
#     
#         elif pdfsize1>=6000:
#             print("Page number "+ str(i+1) + " is not blank.")
#             tempFinal.add_page(page)
#         print(pdfsize1)
#     
#         outputStreamTemp.close()
#         os.remove("paginasize.pdf")
#         tempoutput = PdfWriter()
#     
#     outputStreamTemp1 = open(path_to_watch + "/" + cover_Clean, "wb")
#     tempFinal.write(outputStreamTemp1)
#     outputStreamTemp1.close()
#     sendEmail(cover_Clean)
#     copyToDailyFiles(pdf_name)
#     sendEmailSuccess()   
#     os.remove(path_to_watch + "/" + cover_Clean)
# =============================================================================
