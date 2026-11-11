# -*- coding: utf-8 -*-
"""
Created on Thu Sep 13 20:11:42 2018

@author: z_edwemp_uat
"""
from servicenow_alert import install_exception_hooks as _install_servicenow_exception_hooks
_install_servicenow_exception_hooks()


# -*- coding: utf-8 -*-


import os, time, re
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
# import Tkinter
# import tkMessageBox
# import fnmatch
from PyPDF2 import PdfReader, PdfMerger
# from PyPDF2.pdf import PageObject
import datetime
today_ts = datetime.datetime.now()
today = datetime.datetime.now().date()
import calendar
from datetime import timedelta
import traceback
from servicenow_alert import create_failure_alert
import sys
import re
import stat

import shutil

from reportlab.pdfgen.canvas import Canvas
from pdfrw import PdfReader
from pdfrw.toreportlab import makerl
from pdfrw.buildxobj import pagexobj
from AutomationLog import log_step
from PdfMergeUtils import write_merger_atomically
from GraphEmail import FROM_ADDRESS, send_graph_email

log_step("RegionalScorecard", "START: regional scorecard workflow")

currentMonth = calendar.month_abbr[today_ts.month]
currentMonth=calendar.month_name [list(calendar.month_abbr).index(currentMonth)]
currentDay = str(today_ts.day)
currentYear = str(today_ts.year)
yesterday = today - timedelta(1)
yesterday_string = yesterday.strftime('%Y-%m-%d')
today = today
today_string = today.strftime('%Y-%m-%d')
timestamp = datetime.datetime.strftime(today_ts,"%H-%M-%S")

def servicenow_send_alert(message, description, details):
    return create_failure_alert(
        message, description, details
    )


def createPageNumbers(final_output_dir, final_pdf):

    #cover_dir = "//TJAX2008FS/Entshare/Performance Measurements/Executive Morning Package/EMP Support/Daily Files"
    #cover_pdf = [f for f in os.listdir(cover_dir) if f.startswith("00")]
    #cover_pdf = ''.join(cover_pdf) #converts list to string

    #get the number of pages in cover pdf
    #reader = PdfReader(open(os.path.join(cover_dir, cover_pdf), "rb"))
    #cover_numPages = reader.getNumPages()

    reader = PdfReader(final_pdf)
    pages = [pagexobj(p) for p in reader.pages]

    # Compose new pdf
    canvas = Canvas(final_pdf)
    for page_num, page in enumerate(pages, start=1):
        canvas.setPageSize((page.BBox[2], page.BBox[3]))
        canvas.doForm(makerl(canvas, page))
        # Draw footer
        footer_text = "%s" % (page_num)
        x = 75
        canvas.saveState()
        canvas.setStrokeColorRGB(0, 0, 0)
        canvas.setFont('Times-Roman', 9)
        canvas.drawString(page.BBox[2] - x, 4, footer_text)
        canvas.restoreState()
        canvas.showPage()

    canvas.save()
    final_output = os.path.join(final_output_dir, final_pdf)
    return final_output
#end function

def scalePages(merged_pdf, pdf_name_final):

    original_file = merged_pdf
    temp_path = "//TJAX2008FS/Entshare/Performance Measurements/Executive Morning Package/EMP Support/ExecutePython/"
    temp_folder = os.path.join(temp_path, pdf_name_final)

    os.rename(original_file, temp_folder)

    from PyPDF2 import PdfWriter, PdfReader
    output = PdfWriter()

    fh = open(temp_folder, "rb")
    input1 = PdfReader(fh)

    # Make a simple list of page objects
    pages = []
    for i in range(len(input1.pages)):
        pages.append(input1.pages[i])

    # Scale and add the pages to the output object
    count = 1
    for page in pages:
        page.scale_by(0.91)
        output.add_page(page)
        count += 1

    outDoc = open(original_file, "wb")
    output.write(outDoc)
    outDoc.close()
    fh.close()
    os.remove(temp_folder)
    
def ECM_Merge():
    import importlib.util

    if importlib.util.find_spec("ECM") is None:
        log_step("RegionalScorecard", "SKIP: optional ECM.py module is not installed")
        return

    log_step("RegionalScorecard", "START: import optional ECM workflow")
    import ECM
    log_step("RegionalScorecard", "END: ECM import returned")
    import subprocess
    import sys
    create =  [sys.executable, 'ECM.py']
    
def emailPackage():
    log_step("RegionalScorecard", "START: import and run Email")
    import Email
    log_step("RegionalScorecard", "END: Email import returned")
    import subprocess
    import sys
    create = [sys.executable, 'Email.py']
    
def abort_process():    
    #Copy the file to archive folder, append date to name of file, and timestamp within file. 
    archive_abort_filename = "Automation_" + str(today) + "_" + str(timestamp) + ".txt"
    shutil.copy(os.path.join(abort_path,abort_filename),os.path.join(abort_archive_path, archive_abort_filename))
    file = open((os.path.join(abort_archive_path, archive_abort_filename)), "a")
    file.write("\ntimestamp - " + str(today_ts))
    file.close()

    #Change the text to ON within the Automation text file in ExecutePython Folder for tomorrow's automation to run.
    file = open((os.path.join(abort_path, abort_filename)), "w")
    file.write("ON")
    file.close()
    
    #Send email to notify users that automation has been turned off
    msg1 = MIMEMultipart()
    msg1['From'] = fromaddr
    msg1['To'] = ", ".join(toaddr_abort)
    msg1['Cc'] = ", ".join(cc_abort)
    msg1['Subject'] = "EMP Automation Turned OFF"
    body1 = "EMP Automation has been turned OFF. Please contact Morrison Waye for any issues or concerns."
    msg1.attach(MIMEText(body1, 'plain'))
    text1 = msg1.as_string()
    send_graph_email(msg1, toaddr_abort + cc_abort)

#regional scorecard files dir
region_files_dir = "//TJAX2008FS/Entshare/Performance Measurements/Executive Morning Package/EMP Support/Daily Files/Regional Scorecards"
#all the reports in EMP defined here
regional_mapping_file = "//TJAX2008FS/Entshare/Performance Measurements/Executive Morning Package/EMP Support/ExecutePython/regional_filedefinitions.txt" 
regional_pdfs =  "//TJAX2008FS/Entshare/Performance Measurements/Executive Morning Package/EMP Support/ExecutePython/RegionalScorecard.txt"
abort_path = "//TJAX2008FS/Entshare/Performance Measurements/Executive Morning Package/EMP Support/ExecutePython"
abort_archive_path = "//TJAX2008FS/Entshare/Performance Measurements/Executive Morning Package/EMP Support/ExecutePython/archive"
abort_filename = "Automation.txt"  ##File is updated by user when automation needs to be turned off. 

try:
    # pdf_files = [f for f in os.listdir(region_files_dir) if f.endswith("pdf")]
    log_step(
        "RegionalScorecard",
        f"START: list regional input PDFs in {region_files_dir}",
    )
    pdf_files_orig = [f for f in os.listdir(region_files_dir) if f.endswith("pdf")]
    pdf_files_orig.sort()
    log_step(
        "RegionalScorecard",
        f"END: found {len(pdf_files_orig)} regional input PDF(s)",
    )

    pdf_files = pdf_files_orig.copy()
    pdf_path = []

    for f in pdf_files:
        name = os.path.join(region_files_dir, f)
        pdf_path.append(name)
        
    #check the timestamp of the files to make sure they are current.
    #if timestamp is not current, add to time_list
    time_list = []
    bobj_time = []
    bobj_pdfs_merge = []
    bobj_dir = "//TJAX6000FS/APPDEV/Data Warehouse Public/Business Objects/Morning Package/Regional Scorecards"
    #bobj_dir = "//TJAX2008FS/Entshare/Performance Measurements/Executive Morning Package/EMP Support/Daily Files/Regional Scorecards"
    log_step("RegionalScorecard", f"START: list regional source PDFs in {bobj_dir}")
    bobj_files = [f for f in os.listdir(bobj_dir) if f.endswith("pdf")]
    log_step("RegionalScorecard", f"END: found {len(bobj_files)} regional source PDF(s)")
    
    
    for f in pdf_files:
        name = os.path.join(region_files_dir, f)
        file_time = os.path.getmtime(name)
        file_time1 = datetime.date.fromtimestamp(file_time)
        if file_time1 < today:
            time_list.append(f)
            if f in bobj_files:
                bobj_name = os.path.join(bobj_dir, f)
                file_time = os.path.getmtime(bobj_name)
                file_time1 = datetime.date.fromtimestamp(file_time)
                if file_time1 == today:
                    bobj_pdfs_merge.append(f)
                else:
                    bobj_time.append(f)
                    
                    
    ########################### FILE WATCHER BEGIN #########################################################################
    #Watch regional files till 6:30 AM for today's reports in bobj folder. 
    #If the reports get updated with today's timestamp - use in merge process. 
    #If not found after 5:15 - send email. 
                        
    time1 = datetime.datetime.strptime('06:30:00', '%H:%M:%S')
    time2 = datetime.datetime.strptime(datetime.datetime.strftime(today_ts,"%H:%M:%S"), '%H:%M:%S')
    tsdelta = max(0, (time1 - time2).total_seconds())
    tmdelta = tsdelta / 60
    log_step(
        "RegionalScorecard",
        f"Watcher deadline is 06:30 local time; remaining_minutes={tmdelta:.1f}",
    )
    
    minutes = 0
    i = 0
    
    if time_list and bobj_time :
        log_step(
            "RegionalScorecard",
            f"START: wait for {len(bobj_time)} regional source report(s)",
        )

        servicenow_details = {}
        servicenow_message = 'EMP BOBJ Alert: Regional Scorecard PDF reports have not been updated today' + '\n\n'
        body = 'EMP BOBJ Alert' + '\n' + 'Please check the directory to make sure reports mentioned below are available with todays timestamp and that there no reports open which would cause overwrite issue.' + '\n\n'
        body = body + "Missing Reports: \n\n" + '\n'.join(str(x) for x in bobj_time) + '\n\n'
        servicenow_description = (
            body + "Missing Reports: \n\n"
            + '\n'.join(str(x) for x in time_list)
        )
        servicenow_send_alert(servicenow_message, servicenow_description, servicenow_details)

        while i < len(bobj_time) and minutes < tmdelta:
            n0 = bobj_time[i]
            n = os.path.join(bobj_dir, n0)
            #print n
            t = os.path.getmtime(n)
            t1 = datetime.date.fromtimestamp(t)
            if t1 == today:#
                #print bobj_time[i]
                #print "deleting this file in time list"
                del bobj_time[i]
                bobj_pdfs_merge.append(n0)
    
            while minutes < tmdelta and t1 < today:
                #print minutes
                log_step(
                    "RegionalScorecard",
                    f"WAIT: regional report {n0} is not current; next check in 60 seconds",
                )
                time.sleep(60)
                minutes = minutes + 1
                n0 = bobj_time[i]
                n = os.path.join(bobj_dir, n0)
                t = os.path.getmtime(n)
                t1 = datetime.date.fromtimestamp(t)
                #print t1
                #print minutes
                if t1== today:
                    #print "FOUND PDF - todays timestamp", bobj_time[i], t1
                    #print "deleting this file"
                    del bobj_time[i]
                    bobj_pdfs_merge.append(n0)
                    #print "files remaining after deleting", bobj_time
        log_step(
            "RegionalScorecard",
            f"END: regional source report wait; remaining={len(bobj_time)}",
        )
    
    #################### FILE WATCHER  END #########################################################
                    
                    
    #count the number of files in the Regional Scorecard folder.
    file_count = len(pdf_files)
    
    #declare lists for checking reports in daily files vs filedefinitions.txt
    list_file_number = []
    list_mapping_number = []
    
    
    # make a list out of numbers from the file names in the regional scorecard folder
    i = 0
    for i in range(i,file_count):
        file = pdf_files[i]
        file_number = file[0:2]
        list_file_number.append(file_number)
    
    # count the number of lines in definition file
    log_step("RegionalScorecard", f"START: read regional report mapping {regional_mapping_file}")
    num_lines = sum(1 for line in open(regional_mapping_file))
    
    #create list using mapping file
    Mapping_File_List = open(regional_mapping_file).readlines()
    log_step("RegionalScorecard", f"END: read regional mapping; lines={num_lines}")
    
    #create list of just numbers from the names in definition file
    i = 0
    for i in range(i,num_lines):
        line = Mapping_File_List[i]
        line_number = line[0:2]
    
        list_mapping_number.append(line_number)
    
    #compare the two lists: list_file_number and list_mapping_number to check what files are missing in the daily files folder but mentioned in the definition file.
    set(list_mapping_number).intersection(list_file_number)
    daily_fiiles_missing = list(set(list_mapping_number).difference(list_file_number))
    
    daily_files_missing_list = [i for e in daily_fiiles_missing for i in Mapping_File_List if e in i]
    daily_files_missing_list.sort()
    
    #compare to check if report names are not defined in the mapping file but available in daily files folder.
    mapping_file_missing = [i for i in list_file_number if i not in list_mapping_number]
    
    mapping_file_missing_list = [i for e in mapping_file_missing for i in pdf_files if e in i]
    log_step(
        "RegionalScorecard",
        f"END: regional validation; missing_daily={len(daily_files_missing_list)}, "
        f"missing_mapping={len(mapping_file_missing_list)}, old_reports={len(time_list)}",
    )
    
    #Read file to determine whether to continue automation or to abort. Convert to Uppercase by default. 
    file = open((os.path.join(abort_path, abort_filename)), "r")
    automation_trigger = file.read().upper()
    file.close()
    
    fromaddr = FROM_ADDRESS
    # toaddr = ['Morrison_Waye@csx.com','Michael_Cheatham@csx.com']
    toaddr = ['Srija_Gatla@csx.com']
    # cc = [ 'EDWETL1@CSX.com','BDA@csx.com','BOADMINS@CSX.com','DLTechBusinessIntelligence@csx.com','Srija_Gatla@csx.com']
    cc = ['Srija_Gatla@csx.com']
    # toaddr_abort = ['Morrison_Waye@csx.com','Michael_Cheatham@csx.com' ]
    toaddr_abort = ['Srija_Gatla@csx.com']
    # cc_abort = [ 'EDWETL1@CSX.com','BDA@csx.com','BOADMINS@CSX.com','DLTechBusinessIntelligence@csx.com','Srija_Gatla@csx.com' ]
    cc_abort = ['Srija_Gatla@csx.com']
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = ", ".join(toaddr)
    msg['Cc'] = ", ".join(cc)
    
    
    
    if time_list and bobj_time:
        #root = Tkinter.Tk()
        #root.withdraw()
        #tkMessageBox.showerror
        #tkMessageBox.showerror("Daily Files Folder and BOBJ Folder Error - Old Reports",
        #                       "Reports have not been updated today. Please check the timestamp on reports in Daily Files folder and BOBJ folder ")
    
        msg['Subject'] = "EMP Reports Regional Scorecard Validation Check Failed - Old Reports"
        body = "Reports have not been updated today in Daily Files Folder and BOBJ Folder. \n\nPlease check the timestamp for all the reports in folders: \n'TJAX2008fs\\Entshare\\Performance Measurements\\Executive Morning Package\\EMP Support\\Daily Files' \n'TJAX6000FS\\APPDEV\\Data Warehouse Public\\Business Objects\\Morning Package'" \
               "FYI - Please check if any reports are OPEN which could have caused the BOBJ schedule to fail."
        msg.attach(MIMEText(body, 'plain'))
        text = msg.as_string()
        send_graph_email(msg, toaddr + cc)
        
    
    #if automation_trigger != "ON":
    #    abort_process()
    
        
    
    if not daily_files_missing_list and not mapping_file_missing_list and not bobj_time :
        log_step("RegionalScorecard", "START: merge Regional Scorecards report")
        merger = PdfMerger()
        reg_list = open(regional_pdfs).readlines()
        reg_list1 = [(reg.strip()) for reg in reg_list]
        reg_files = [i for e in reg_list1 for i in pdf_files if e in i]
        #ehh_files = [i for e in ehh_list1 for i in pdf_path if e in i]
        # reg_files.sort()
    
        reg_files_clean = []
        [reg_files_clean.append(x) for x in reg_files if x not in reg_files_clean]  # remove duplicates
    
        #ehh_output_dir = "//TJAX2008FS/Entshare/Performance Measurements/Executive Morning Package/EMP Support/EHH"
        reg_output_dir = "//TJAX2008FS/Entshare/Performance Measurements/Executive Morning Package/EMP Support/RegionalScorecards"
        
        for filename in reg_files_clean:
            if filename not in bobj_pdfs_merge:
                source_path = region_files_dir+'/'+ filename
            elif filename in bobj_pdfs_merge:
                source_path = bobj_dir+'/'+ filename
            log_step("RegionalScorecard", f"START: append regional input {source_path}")
            merger.append(source_path)
            log_step("RegionalScorecard", f"END: append regional input {source_path}")
    
        #pdf_name = " - Executive Morning Package.pdf"
        #pdf_name_final = currentMonth + " " + currentDay + ", " + currentYear + pdf_name
    
        pdf_name = "Regional Scorecards - "
        pdf = ".pdf"
        pdf_name_final = pdf_name + currentMonth + " " + currentDay + ", " + currentYear + pdf
    
        write_merger_atomically(
            merger,
            os.path.join(reg_output_dir, pdf_name_final),
            "RegionalScorecard",
        )
        log_step(
            "RegionalScorecard",
            f"END: merged Regional Scorecards report {os.path.join(reg_output_dir, pdf_name_final)}",
        )
    
        reg_final_pdf = os.path.join(reg_output_dir, pdf_name_final)

        # To provide write permission to the file name- 09/01/2023 6:00 AM, change made by Z8182
        # Based on the CR - CHG0038130

        os.chmod(reg_final_pdf, stat.S_IRWXU)
        time.sleep(5)
    
        #add page number to the merged file
        reg_merged_file = createPageNumbers(reg_output_dir,reg_final_pdf)
    
        #scale pages in pdf
        scalePages(reg_merged_file, pdf_name_final)
        log_step("RegionalScorecard", "END: Regional Scorecards report")
        
        if not time_list:
             
            with open("//TJAX2008FS/Entshare/Performance Measurements/Executive Morning Package/EMP Support/ExecutePython/logs/RegionalScorecardMergeSuccess.txt",
                "a") as text_file:
                text_file.write("Regional Scorecard merged successfuly. " + str(today_ts) + "\n")
            
            msg['Subject'] = "Regional Scorecard Reports Validation and Merge - Completed Successfully"
            body = "Reports have been merged successfully into their respective folders. \n\nPlease check the merged reports in folder: 'TJAX2008fs\\Entshare\\Performance Measurements\\Executive Morning Package\\EMP Support\\RegionalScorecards'."
            msg.attach(MIMEText(body, 'plain'))
            text = msg.as_string()
            log_step("RegionalScorecard", "START: send regional merge success notification")
            send_graph_email(msg, toaddr + cc)
            log_step("RegionalScorecard", "END: regional merge success notification sent")
            ECM_Merge()
            emailPackage()
        elif time_list and not bobj_time:
            
            with open("//TJAX2008FS/Entshare/Performance Measurements/Executive Morning Package/EMP Support/ExecutePython/logs/RegionalScorecardMergeSuccess.txt",
                "a") as text_file:
                text_file.write("Regional Scorecard merged successfuly. " + str(today_ts) + "\n")
                
            msg['Subject'] = "Regional Scorecards - Completed using file(s) from BOBJ folder. Daily Files Folder - Found OLD Reports"
            body = "Reports have been merged successfully into their respective folders. \n\nPlease check the merged reports in folder: 'TJAX2008fs\\Entshare\\Performance Measurements\\Executive Morning Package\\EMP Support'." \
                    "\n\nFYI - There are OLD reports in Daily Files Folder. Please check if they are any OPEN files which may have caused BOBJ schedule to fail. "
            msg.attach(MIMEText(body, 'plain'))
            text = msg.as_string()
            log_step("RegionalScorecard", "START: send regional merge notification")
            send_graph_email(msg, toaddr + cc)
            log_step("RegionalScorecard", "END: regional merge notification sent")
            ECM_Merge()
            emailPackage()
            
    
    #Alert users if daily_files_missing has values (means that reports are missing in daily files folder but present in filedefinitions.txt)
    elif daily_files_missing_list:
        #message box
        #root = Tkinter.Tk()
        #root.withdraw()
        #tkMessageBox.showerror("Error - Missing Reports in Daily Files folder", "EMP Reports Validation Check \n\nMissing Reports in Daily Files folder but specified in filedefinitions.txt : \n\n"
        #                       + '\n'.join(str(x) for x in daily_files_missing_list))
        #email
        msg['Subject'] = "EMP Automation : Regional Scorecard Reports Validation Check Failed - Missing Reports"
        body = "There are missing reports in the Daily Files folder, but specified in 'regional_filedefinitions.txt' (in ExecutePython folder). Please contact BIG_Support (Big_Support@csx.com) for more information \n\nPlease check the listed reports below in folder: 'TJAX2008fs\\Entshare\\Performance Measurements\\Executive Morning Package\\EMP Support\\Daily Files' to make sure they are available. \n\n" \
               + '\n'.join(str(x) for x in daily_files_missing_list)
        msg.attach(MIMEText(body, 'plain'))
        text = msg.as_string()
        send_graph_email(msg, toaddr + cc)
    
    #Alert users if the definition file doesn't have all the reports specified that daily files folder has.
    elif mapping_file_missing_list:
        # message box
        #root = Tkinter.Tk()
        #root.withdraw()
        #tkMessageBox.showerror("Error - FileDefinitions.txt does not have all the reports specified",
        #                     "EMP Reports Validation Check \n\nPlease add the missing report name(s) to 'filedefinitions.txt' (in ExecutePython folder) which are part of the EMP package : \n\n"
        #                     + '\n'.join(str(x) for x in mapping_file_missing_list))
        # email
        msg['Subject'] = "EMP Automation: Regional Scorecard Reports Validation Check Failed - regional_filedefinitions.txt does not have all the report names"
        body = "Report name(s) is missing in text file 'regional_filedefinitions.txt' ! Please add the report name(s) to the file in ExecutePython folder. \n\n" + '\n'.join(
            str(x) for x in mapping_file_missing_list)
        msg.attach(MIMEText(body, 'plain'))
        text = msg.as_string()
        send_graph_email(msg, toaddr + cc)

    log_step("RegionalScorecard", "END: regional scorecard workflow")
except KeyboardInterrupt:
    log_step(
        "RegionalScorecard",
        "INTERRUPTED: regional workflow stopped by user\n" + traceback.format_exc(),
    )
    raise
except Exception as e:
    log_step("RegionalScorecard", f"ERROR: {type(e).__name__}: {e}\n{traceback.format_exc()}")
    servicenow_details = {}
    servicenow_details['File Name'] = os.path.basename(sys.argv[0])
    print(e)
    print(traceback.print_exc())
    servicenow_message = 'EMP - Python Coding Error'
    servicenow_description = str(e) + '\n\n'
    servicenow_description = servicenow_description + traceback.format_exc()
    servicenow_send_alert(servicenow_message, servicenow_description, servicenow_details)
    raise
