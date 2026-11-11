# -*- coding: utf-8 -*-
from servicenow_alert import install_exception_hooks as _install_servicenow_exception_hooks
_install_servicenow_exception_hooks()

import os, time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
# import Tkinter
# import tkMessageBox
# import fnmatch
from PyPDF2 import PdfMerger
# from PyPDF2.pdf import PageObject
import datetime
today_ts = datetime.datetime.now()
today = datetime.datetime.now().date()
import calendar
from datetime import timedelta
from servicenow_alert import create_failure_alert
import traceback
import sys

import shutil
import stat
import tempfile
from AutomationLog import log_step
from PdfMergeUtils import write_merger_atomically

from reportlab.pdfgen.canvas import Canvas
from pdfrw import PdfReader
from pdfrw.toreportlab import makerl
from pdfrw.buildxobj import pagexobj
from GraphEmail import FROM_ADDRESS, send_graph_email

log_step("MergePdfs", "START: EMP report merge")

#current date setup for file names
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


#page number funtion - called during merge process
def createPageNumbers(final_output_dir, final_pdf):
    log_step("MergePdfs", f"START: add page numbers to {final_pdf}")
    cover_dir = "//TJAX2008FS/Entshare/Performance Measurements/Executive Morning Package/EMP Support/Daily Files"

    cover_pdfs = [
        filename
        for filename in os.listdir(cover_dir)
        if filename.startswith("00 Cover Page") and filename.endswith(".pdf")
    ]
    if len(cover_pdfs) != 1:
        raise FileNotFoundError(
            f"Expected exactly one cover PDF in {cover_dir}; found {len(cover_pdfs)}."
        )
    cover_pdf = cover_pdfs[0]
    cover_path = os.path.join(cover_dir, cover_pdf)

    log_step("MergePdfs", f"START: read cover PDF {cover_path}")
    with open(cover_path, "rb") as cover_file:
        cover_num_pages = len(PdfReader(cover_file).pages)
    log_step("MergePdfs", f"END: read cover PDF {cover_pdf}; pages={cover_num_pages}")

    log_step("MergePdfs", f"START: read report for numbering {final_pdf}")
    reader = PdfReader(final_pdf)
    pages = [pagexobj(page) for page in reader.pages]
    log_step("MergePdfs", f"END: read report for numbering; pages={len(pages)}")

    final_output = (
        final_pdf
        if os.path.isabs(final_pdf)
        else os.path.join(final_output_dir, final_pdf)
    )
    file_descriptor, numbered_path = tempfile.mkstemp(
        prefix="emp-numbered-", suffix=".pdf"
    )
    os.close(file_descriptor)
    operation_error = None

    try:
        include_cover = not (
            "Terminal Scorecard" in final_pdf or "Definitions" in final_pdf
        )
        pages_to_number = pages[cover_num_pages:] if include_cover else pages
        log_step(
            "MergePdfs",
            f"START: create numbered intermediate PDF {numbered_path}; "
            f"pages_to_number={len(pages_to_number)}",
        )
        canvas = Canvas(numbered_path)
        for page_num, page in enumerate(pages_to_number, start=1):
            log_step(
                "MergePdfs",
                f"START: number page {page_num}/{len(pages_to_number)} in {final_pdf}",
            )
            canvas.setPageSize((page.BBox[2], page.BBox[3]))
            canvas.doForm(makerl(canvas, page))
            canvas.saveState()
            canvas.setStrokeColorRGB(0, 0, 0)
            canvas.setFont("Times-Roman", 9)
            canvas.drawString(page.BBox[2] - 75, 4, str(page_num))
            canvas.restoreState()
            canvas.showPage()
            log_step(
                "MergePdfs",
                f"END: number page {page_num}/{len(pages_to_number)} in {final_pdf}",
            )
        canvas.save()
        log_step("MergePdfs", f"END: numbered intermediate PDF {numbered_path}")

        merger = PdfMerger()
        if include_cover:
            log_step("MergePdfs", f"START: append cover PDF {cover_path}")
            merger.append(cover_path)
            log_step("MergePdfs", f"END: append cover PDF {cover_path}")
        log_step("MergePdfs", f"START: append numbered report {numbered_path}")
        merger.append(numbered_path)
        log_step("MergePdfs", f"END: append numbered report {numbered_path}")
        if os.path.exists(final_output):
            os.chmod(final_output, stat.S_IRWXU)
        write_merger_atomically(merger, final_output, "MergePdfs")
        log_step("MergePdfs", f"END: page-numbered output ready {final_output}")
        return final_output
    except BaseException as error:
        operation_error = error
        log_step(
            "MergePdfs",
            f"ERROR: page numbering failed for {final_pdf}: "
            f"{type(error).__name__}: {error}\n{traceback.format_exc()}",
        )
        raise
    finally:
        if os.path.exists(numbered_path):
            log_step("MergePdfs", f"START: remove numbered intermediate {numbered_path}")
            try:
                os.remove(numbered_path)
                log_step("MergePdfs", f"END: removed numbered intermediate {numbered_path}")
            except OSError as cleanup_error:
                if operation_error is None:
                    raise
                log_step(
                    "MergePdfs",
                    f"WARNING: could not remove numbered intermediate {numbered_path}: "
                    f"{cleanup_error}. Original error remains "
                    f"{type(operation_error).__name__}.",
                )
#end function

def scalePages(merged_pdf, pdf_name_final):

    original_file = merged_pdf
    log_step("MergePdfs", f"START: scale merged PDF {original_file}")
    temp_path = "//TJAX2008FS/Entshare/Performance Measurements/Executive Morning Package/EMP Support/ExecutePython/"
    temp_folder = os.path.join(temp_path, pdf_name_final)

    log_step("MergePdfs", f"START: move source PDF to scaling temp file {temp_folder}")
    os.rename(original_file, temp_folder)
    log_step("MergePdfs", f"END: moved source PDF to scaling temp file {temp_folder}")

    from PyPDF2 import PdfWriter, PdfReader
    output = PdfWriter()

    fh = open(temp_folder, "rb")
    input1 = PdfReader(fh)
    log_step("MergePdfs", f"Read PDF for scaling; pages={len(input1.pages)}")

    # Make a simple list of page objects
    pages = []
    for i in range(len(input1.pages)):
        pages.append(input1.pages[i])

    # Scale and add the pages to the output object
    count = 1
    for page in pages:
        log_step("MergePdfs", f"START: scale page {count}/{len(pages)} in {pdf_name_final}")
        page.scale_by(0.91)
        output.add_page(page)
        log_step("MergePdfs", f"END: scale page {count}/{len(pages)} in {pdf_name_final}")
        count += 1

    log_step("MergePdfs", f"START: write scaled PDF {original_file}")
    outDoc = open(original_file, "wb")
    output.write(outDoc)
    outDoc.close()
    log_step("MergePdfs", f"END: wrote scaled PDF {original_file}")
    fh.close()
    os.remove(temp_folder)
    log_step("MergePdfs", f"END: scaled PDF complete {original_file}")
    
def regionalScorecard():
    log_step("MergePdfs", "START: import and run RegionalScorecard")
    import RegionalScorecard
    log_step("MergePdfs", "END: RegionalScorecard import returned")
    import subprocess
    import sys
    create = [sys.executable, 'RegionalScorecard.py']
#    
#Called when abort_trigger is OFF
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


#define folders and files needed for the script
daily_files_dir = "//TJAX2008FS/Entshare/Performance Measurements/Executive Morning Package/EMP Support/Daily Files" #all the morning reports are here
files_dir = "//TJAX2008FS/Entshare/Performance Measurements/Executive Morning Package/EMP Support/Daily Files" #all the morning reports are here
mapping_file = "//TJAX2008FS/Entshare/Performance Measurements/Executive Morning Package/EMP Support/ExecutePython/filedefinitions.txt" #all the reports in EMP defined here
ehh_pdfs =  "//TJAX2008FS/Entshare/Performance Measurements/Executive Morning Package/EMP Support/ExecutePython/EHH.txt"
revenue_pdfs = "//TJAX2008FS/Entshare/Performance Measurements/Executive Morning Package/EMP Support/ExecutePython/Revenue.txt"
nonrevenue_pdfs = "//TJAX2008FS/Entshare/Performance Measurements/Executive Morning Package/EMP Support/ExecutePython/NonRevenue.txt"
nonrevenueECM_pdfs = "//TJAX2008FS/Entshare/Performance Measurements/Executive Morning Package/EMP Support/ExecutePython/NonRevenueECM.txt"
terminalscorecard_pdfs = "//TJAX2008FS/Entshare/Performance Measurements/Executive Morning Package/EMP Support/ExecutePython/TerminalScorecard.txt"
empdefs_pdfs = "//TJAX2008FS/Entshare/Performance Measurements/Executive Morning Package/EMP Support/ExecutePython/EMPDefinitions.txt"
abort_path = "//TJAX2008FS/Entshare/Performance Measurements/Executive Morning Package/EMP Support/ExecutePython"
abort_archive_path = "//TJAX2008FS/Entshare/Performance Measurements/Executive Morning Package/EMP Support/ExecutePython/archive"
abort_filename = "Automation.txt"  ##File is updated by user when automation needs to be turned off. 
cover_archive_path = "//TJAX2008FS/Entshare/Performance Measurements/Executive Morning Package/EMP Support/Daily Files/Archive"

try: 
    #read and sort files that end with .pdf
    log_step("MergePdfs", f"START: list daily PDFs in {files_dir}")
    pdf_files = [f for f in os.listdir(files_dir) if f.endswith("pdf")]
    pdf_files.sort()
    log_step("MergePdfs", f"END: found {len(pdf_files)} daily PDFs")
    
    #check for duplicate numbers
    i = 0
    num_list = []
    for f in pdf_files:
        num_list.append(pdf_files[i][:2])
        i = i+1
    unique_list = list(set(num_list))
    unique_list.sort()
    
    pdf_path = []
    
    for f in pdf_files:
        name =  os.path.join(files_dir, f)
        pdf_path.append(name)
    
    #check the timestamp of the files to make sure they are current.
    #if timestamp is not current, add to time_list
    time_list = []
    bobj_time = []
    bobj_pdfs_merge = []
    bobj_dir = "//TJAX6000FS/APPDEV/Data Warehouse Public/Business Objects/Morning Package"
    log_step("MergePdfs", f"START: list source PDFs in {bobj_dir}")
    bobj_files = [f for f in os.listdir(bobj_dir) if f.endswith("pdf")]
    log_step("MergePdfs", f"END: found {len(bobj_files)} source PDFs")
    
    #check timestamp of each report in DailyFiles folder.
    for f in pdf_files:
        log_step("MergePdfs", f"START: check report timestamp {f}")
        if f == "30 Engineering Daily.pdf":
            name = os.path.join(files_dir, f)
            file_time = os.path.getmtime(name)
            file_time1 = datetime.date.fromtimestamp(file_time)
            if file_time1 < yesterday:
                time_list.append(f)
                if f in bobj_files:
                    bobj_name = os.path.join(bobj_dir, f)
                    file_time = os.path.getmtime(bobj_name)
                    file_time1 = datetime.date.fromtimestamp(file_time)
                    if file_time1 >= yesterday:
                        bobj_pdfs_merge.append(f)
                    else:
                        bobj_time.append(f)
    
        elif not("Cover Page" in f) and f != "30 Engineering Daily.pdf" and f != "85 Executive Morning Package Complete Definitions.pdf" and f!= "90 Executive Morning Package Definitions - 2 pager.pdf" and f!="Archive" and f!="Thumbs.db":
            name = os.path.join(files_dir, f)
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
        elif "Cover Page" in f:
            name = os.path.join(files_dir, f)
            file_time = os.path.getmtime(name)
            file_time1 = datetime.date.fromtimestamp(file_time)
            if file_time1 < yesterday:
                time_list.append(f)
        log_step("MergePdfs", f"END: checked report timestamp {f}")
            
    
    ## if cover page is part of time_list then move to archive and delete from time_list - just means there is an older cover page that did not get deleted at the end of sending emp
    index1 = []
    for s in time_list:
        if "00 Cover Page" in s:
            index = time_list.index(s)
            index1.append(index)
            cover_page = ''.join(s)
            log_step("MergePdfs", f"START: archive old cover PDF {cover_page}")
            shutil.move(cover_page, cover_archive_path)
            log_step("MergePdfs", f"END: archived old cover PDF {cover_page}")
            
    
    for index in sorted(index1, reverse=True):
        del time_list[index]
    
    ########################### FILE WATCHER BEGIN #########################################################################
    #Watch files till 5:15 AM for today's reports in bobj folder. 
    #If the reports get updated with today's timestamp - use in merge process. 
    #If not found after 5:15 - send email. 
                        
    time1 = datetime.datetime.strptime('06:30:00', '%H:%M:%S')
    time2 = datetime.datetime.strptime(datetime.datetime.strftime(today_ts,"%H:%M:%S"), '%H:%M:%S')
    tsdelta = max(0, (time1 - time2).total_seconds())
    tmdelta = tsdelta / 60
    log_step(
        "MergePdfs",
        f"Watcher deadline is 06:30 local time; remaining_minutes={tmdelta:.1f}",
    )
    
    minutes = 0
    i = 0
    
    
    if time_list and bobj_time:
        log_step(
            "MergePdfs",
            f"START: wait for {len(bobj_time)} source report(s); "
            f"{len(time_list)} daily report(s) are old",
        )

        servicenow_details = {}
        servicenow_message = 'EMP BOBJ Alert: PDF reports have not been updated today' + '\n\n'
        body = 'EMP BOBJ Alert' + '\n' + 'Please check the directory to make sure reports mentioned below are available with todays timestamp and that there no reports open which would cause overwrite issue.' + '\n\n'
        servicenow_description = (
            body + "Missing Reports: \n\n"
            + '\n'.join(str(x) for x in time_list)
        )
        servicenow_send_alert(
            servicenow_message, servicenow_description, servicenow_details
        )

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
                log_step("MergePdfs", f"WAIT: source report {n0} is not current; next check in 60 seconds")
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
            "MergePdfs",
            f"END: source report wait finished; remaining={len(bobj_time)}",
        )
        log_step(
            "MergePdfs",
            f"END: source report wait finished; remaining={len(bobj_time)}",
        )
    
    #################### FILE WATCHER  END #########################################################
                    
    #count the number of files in the Daily Files folder.
    file_count = len(pdf_files)
    
    #declare lists for checking reports in daily files vs filedefinitions.txt
    list_file_number = []
    list_mapping_number = []
    
    # make a list out of numbers from the file names in the daily files folder
    i = 0
    for i in range(i,file_count):
        file = pdf_files[i]
        file_number = file[0:2]
        list_file_number.append(file_number)
    
    # count the number of lines in definition file
    log_step("MergePdfs", f"START: read report mapping {mapping_file}")
    log_step("MergePdfs", f"START: read report mapping {mapping_file}")
    num_lines = sum(1 for line in open(mapping_file))
    
    #create list using mapping file
    Mapping_File_List = open(mapping_file).readlines()
    log_step("MergePdfs", f"END: read report mapping; lines={num_lines}")
    log_step("MergePdfs", f"END: read report mapping; lines={num_lines}")
    
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
        "MergePdfs",
        f"END: report validation; missing_daily={len(daily_files_missing_list)}, "
        f"missing_mapping={len(mapping_file_missing_list)}, old_reports={len(time_list)}",
    )
    log_step(
        "MergePdfs",
        f"END: report validation; missing_daily={len(daily_files_missing_list)}, "
        f"missing_mapping={len(mapping_file_missing_list)}, old_reports={len(time_list)}",
    )
    
        
        
    #Read file to determine whether to continue automation or to abort. Convert to Uppercase by default. 
    file = open((os.path.join(abort_path, abort_filename)), "r")
    automation_trigger = file.read().upper()
    file.close()
    
    #email setup
    fromaddr = FROM_ADDRESS
    toaddr = [ 'Morrison_Waye@csx.com','Michael_Cheatham@csx.com']
    # toaddr = ['Srija_Gatla@csx.com']
    cc = ['EDWETL1@CSX.com','BDA@csx.com','BOADMINS@CSX.com','DLTechBusinessIntelligence@csx.com','Srija_Gatla@csx.com' ]
    # cc = ['Srija_Gatla@csx.com']

    toaddr_abort = ['Srija_Gatla@csx.com','Sunkara_ChandanaSudha@csx.com']
    # toaddr_abort = ['Srija_Gatla@csx.com']
    cc_abort = ['EDWETL1@CSX.com','Srija_Gatla@csx.com' ]
    # cc_abort = ['Srija_Gatla@csx.com']
    
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = ", ".join(toaddr)
    msg['Cc'] = ", ".join(cc)
    log_step("MergePdfs", "START: connect SMTP for merge status notifications")
    log_step("MergePdfs", "END: connected SMTP for merge status notifications")
    
    if time_list and bobj_time:
        #root = Tkinter.Tk()
        #root.withdraw()
        #tkMessageBox.showerror
        #tkMessageBox.showerror("Daily Files Folder and BOBJ Folder Error - Old Reports",
        #                       "Reports have not been updated today. Please check the timestamp on reports in Daily Files folder and BOBJ folder ")
    
        msg['Subject'] = "EMP Reports Validation Check Failed - Old Reports"
        body = "Reports have not been updated today in Daily Files Folder and BOBJ Folder. \n\nPlease check the timestamp for all the reports in folders: \n'TJAX2008fs\\Entshare\\Performance Measurements\\Executive Morning Package\\EMP Support\\Daily Files' \n'TJAX6000FS\\APPDEV\\Data Warehouse Public\\Business Objects\\Morning Package'" \
               "FYI - Please check if any reports are OPEN which could have caused the BOBJ schedule to fail."
        msg.attach(MIMEText(body, 'plain'))
        text = msg.as_string()
        log_step("MergePdfs", "START: send old-report notification")
        send_graph_email(msg, toaddr + cc)
        log_step("MergePdfs", "END: old-report notification sent")
    
    #if automation_trigger != "ON":
    #    abort_process()
    
    #Merge Files if all the lists are empty
    log_step(
        "MergePdfs",
        "Validation result: "
        f"missing_daily={len(daily_files_missing_list)}, "
        f"missing_mapping={len(mapping_file_missing_list)}, "
        f"waiting_for_source={len(bobj_time)}",
    )
    if not daily_files_missing_list and not mapping_file_missing_list and not bobj_time:
        #root = Tkinter.Tk()
        #root.withdraw()
        #tkMessageBox.showinfo("Validation Check", "EMP Reports Validation Check - Successful")
        
        log_step("MergePdfs", "START: Terminal Scorecard report")
        #####Terminal Scorecard merge files#
        merger2 = PdfMerger()
        terminalscorecard_list = open(terminalscorecard_pdfs).readlines()
        terminalscorecard_list1 = [(terminalscorecard.strip()) for terminalscorecard in terminalscorecard_list]
        terminalscorecard_files = [i for e in terminalscorecard_list1 for i in pdf_files if e in i]
        terminalscorecard_files.sort()
        terminalscorecard_files_clean = []
        [terminalscorecard_files_clean.append(x) for x in terminalscorecard_files if x not in terminalscorecard_files_clean] #remove duplicates
    
        #nonrevenue_output_dir = "//TJAX2008FS/Entshare/Performance Measurements/Executive Morning Package/EMP Support/Non-Revenue"####Terminal Scorecard merge files
        merger2 = PdfMerger()
        terminalscorecard_list = open(terminalscorecard_pdfs).readlines()
        terminalscorecard_list1 = [(terminalscorecard.strip()) for terminalscorecard in terminalscorecard_list]
        terminalscorecard_files = [i for e in terminalscorecard_list1 for i in pdf_files if e in i]
        terminalscorecard_files.sort()
        terminalscorecard_files_clean = []
        [terminalscorecard_files_clean.append(x) for x in terminalscorecard_files if x not in terminalscorecard_files_clean] #remove duplicates
    
        terminalscorecard_output_dir = "//TJAX2008FS/Entshare/Performance Measurements/Executive Morning Package/EMP Support/TerminalScorecard"
    
        #for filename in nonrevenue_files_clean:
        #    merger2.append(PdfReader(os.path.join(files_dir, filename), "rb"))
    
        for filename in terminalscorecard_files_clean:
            if filename not in bobj_pdfs_merge:
                source_path = files_dir+'/'+filename
            elif filename in bobj_pdfs_merge:
                source_path = bobj_dir+'/'+filename
            log_step("MergePdfs", f"START: append Terminal Scorecard input {source_path}")
            merger2.append(source_path)
            log_step("MergePdfs", f"END: append Terminal Scorecard input {source_path}")
    
        pdf_name = "Executive Morning Package - Terminal Scorecard - "
        pdf_name_final = pdf_name + currentMonth + " " + currentDay + ", " + currentYear + ".pdf"
    
        write_merger_atomically(
            merger2,
            os.path.join(terminalscorecard_output_dir, pdf_name_final),
            "MergePdfs",
        )
    
        terminalscorecard_final_pdf = os.path.join(terminalscorecard_output_dir, pdf_name_final)

        # To provide write permission to the file name- 09/01/2023 6:00 AM, change made by Z8182
        # Based on the CR - CHG0038130

        os.chmod(terminalscorecard_final_pdf, stat.S_IRWXU)

        time.sleep(5)

    
        terminalscorecard_merged_file = createPageNumbers(terminalscorecard_output_dir,terminalscorecard_final_pdf)
    
        scalePages(terminalscorecard_merged_file, pdf_name_final)
        log_step("MergePdfs", "END: Terminal Scorecard report")
    
        #tkMessageBox.showinfo("Merge Files Completed", "Terminal Scorecard - Merge Successful")
    
        log_step("MergePdfs", "START: EMP Definitions report")
        ####EMP Defintions merge files
        merger2 = PdfMerger()
        empdefs_list = open(empdefs_pdfs).readlines()
        empdefs_list1 = [(empdefs.strip()) for empdefs in empdefs_list]
        empdefs_files = [i for e in empdefs_list1 for i in pdf_files if e in i]
        empdefs_files.sort()
        empdefs_files_clean = []
        [empdefs_files_clean.append(x) for x in empdefs_files if x not in empdefs_files_clean]  # remove duplicates
    
        empdefs_output_dir = "//TJAX2008FS/Entshare/Performance Measurements/Executive Morning Package/EMP Support/EMPDefintions"
    
        # for filename in nonrevenue_files_clean:
        #    merger2.append(PdfReader(os.path.join(files_dir, filename), "rb"))
    
        for filename in empdefs_files_clean:
            if filename not in bobj_pdfs_merge:
                source_path = files_dir+'/'+ filename
            elif filename in bobj_pdfs_merge:
                source_path = bobj_dir+'/'+ filename
            log_step("MergePdfs", f"START: append EMP Definitions input {source_path}")
            merger2.append(source_path)
            log_step("MergePdfs", f"END: append EMP Definitions input {source_path}")
    
        pdf_name = "Executive Morning Package - EMP Definitions - "
        pdf_name_final = pdf_name + currentMonth + " " + currentDay + ", " + currentYear + ".pdf"
    
        write_merger_atomically(
            merger2, os.path.join(empdefs_output_dir, pdf_name_final), "MergePdfs"
        )
    
        empdefs_final_pdf = os.path.join(empdefs_output_dir, pdf_name_final)

        # To provide write permission to the file name- 09/01/2023 6:00 AM, change made by Z8182
        # Based on the CR - CHG0038130

        os.chmod(empdefs_final_pdf, stat.S_IRWXU)
        time.sleep(5)
    
        empdefs_merged_file = createPageNumbers(empdefs_output_dir,empdefs_final_pdf)
    
        scalePages(empdefs_merged_file, pdf_name_final)
        log_step("MergePdfs", "END: EMP Definitions report")
    
        #tkMessageBox.showinfo("Merge Files Completed", "EMP Definitions - Merge Successful")
    
        log_step("MergePdfs", "START: EHH report")
        #EHH Merge Files
        merger = PdfMerger()
        ehh_list = open(ehh_pdfs).readlines()
        ehh_list1 = [(ehh.strip()) for ehh in ehh_list]
        ehh_files = [i for e in ehh_list1 for i in pdf_files if e in i]
        #ehh_files = [i for e in ehh_list1 for i in pdf_path if e in i]
        ehh_files.sort()
    
        ehh_files_clean = []
        [ehh_files_clean.append(x) for x in ehh_files if x not in ehh_files_clean]  # remove duplicates
    
        #ehh_output_dir = "//TJAX2008FS/Entshare/Performance Measurements/Executive Morning Package/EMP Support/EHH"
        ehh_output_dir = "//TJAX2008FS/Entshare/Performance Measurements/Executive Morning Package/EMP Support/EHH"
    
        for filename in ehh_files_clean:
            if filename not in bobj_pdfs_merge:
                source_path = files_dir+'/'+ filename
            elif filename in bobj_pdfs_merge:
                source_path = bobj_dir+'/'+ filename
            log_step("MergePdfs", f"START: append EHH input {source_path}")
            merger.append(source_path)
            log_step("MergePdfs", f"END: append EHH input {source_path}")
    
        #pdf_name = " - Executive Morning Package.pdf"
        #pdf_name_final = currentMonth + " " + currentDay + ", " + currentYear + pdf_name
    
        pdf_name = "Executive Morning Package - Revenue - "
        pdf = ".pdf"
        pdf_name_final = pdf_name + currentMonth + " " + currentDay + ", " + currentYear + pdf
    
        write_merger_atomically(
            merger, os.path.join(ehh_output_dir, pdf_name_final), "MergePdfs"
        )
    
        ehh_final_pdf = os.path.join(ehh_output_dir, pdf_name_final)

        # To provide write permission to the file name- 09/01/2023 6:00 AM, change made by Z8182
        # Based on the CR - CHG0038130

        os.chmod(ehh_final_pdf, stat.S_IRWXU)
        time.sleep(5)
    
        #add page number to the merged file
        ehh_merged_file = createPageNumbers(ehh_output_dir,ehh_final_pdf)
    
        #scale pages in pdf
        scalePages(ehh_merged_file, pdf_name_final)
        log_step("MergePdfs", "END: EHH report")
    
        #tkMessageBox.showinfo("Merge Files Completed", "EHH Version Morning Package - Merge Successful")
    
        log_step("MergePdfs", "START: Revenue Core report")
        #Revenue Morning Package merge files
        merger1 = PdfMerger()
        revenue_list = open(revenue_pdfs).readlines()
        revenue_list1 = [(revenue.strip()) for revenue in revenue_list]
        revenue_files = [i for e in revenue_list1 for i in pdf_files if e in i]
        for item in revenue_files:
            if item.startswith("90"):
                revenue_files.remove(item)
        revenue_files.sort()
        revenue_files_clean = []
        [revenue_files_clean.append(x) for x in revenue_files if x not in revenue_files_clean]  # remove duplicates
    
        #revenue_output_dir = "//TJAX2008FS/Entshare/Performance Measurements/Executive Morning Package/EMP Support/Revenue Secure"
        revenue_output_dir="//TJAX2008FS/Entshare/Performance Measurements/Executive Morning Package/EMP Support/Revenue Secure"
    
        #for filename in revenue_files_clean:
        #    merger1.append(PdfReader(os.path.join(files_dir, filename), "rb"))
        #    pdf_name = "Executive Morning Package - Revenue - "
        #    pdf = ".pdf"
        #    pdf_name_final = pdf_name + currentMonth + " " + currentDay + ", " + currentYear + pdf
    
        for filename in revenue_files_clean:
            if filename not in bobj_pdfs_merge:
                source_path = files_dir+'/'+ filename
            elif filename in bobj_pdfs_merge:
                source_path = bobj_dir+'/'+ filename
            log_step("MergePdfs", f"START: append Revenue input {source_path}")
            merger1.append(source_path)
            log_step("MergePdfs", f"END: append Revenue input {source_path}")
    
        pdf_name = "Executive Morning Package - Revenue Core - "
        pdf = ".pdf"
        pdf_name_final = pdf_name + currentMonth + " " + currentDay + ", " + currentYear + pdf
    
        write_merger_atomically(
            merger1, os.path.join(revenue_output_dir, pdf_name_final), "MergePdfs"
        )
    
        revenue_final_pdf = os.path.join(revenue_output_dir, pdf_name_final)

        # To provide write permission to the file name- 09/01/2023 6:00 AM, change made by Z8182
        # Based on the CR - CHG0038130

        os.chmod(revenue_final_pdf, stat.S_IRWXU)
        time.sleep(5)
    
        revenue_merged_file = createPageNumbers(revenue_output_dir,revenue_final_pdf)
    
        scalePages(revenue_merged_file, pdf_name_final)
        log_step("MergePdfs", "END: Revenue Core report")
    
        #tkMessageBox.showinfo("Merge Files Completed", "Revenue Morning Package - Merge Successful")
    
        log_step("MergePdfs", "START: Non-Revenue Core report")
        # Non-Revenue Morning Package merge files
        merger2 = PdfMerger()
        nonrevenue_list = open(nonrevenue_pdfs).readlines()
        nonrevenue_list1 = [(nonrev.strip()) for nonrev in nonrevenue_list]
        nonrevenue_files = [i for e in nonrevenue_list1 for i in pdf_files if e in i]
        nonrevenue_files.sort()
        nonrevenue_files_clean = []
        [nonrevenue_files_clean.append(x) for x in nonrevenue_files if x not in nonrevenue_files_clean] #remove duplicates
    
        #nonrevenue_output_dir = "//TJAX2008FS/Entshare/Performance Measurements/Executive Morning Package/EMP Support/Non-Revenue"
        nonrevenue_output_dir = "//TJAX2008FS/Entshare/Performance Measurements/Executive Morning Package/EMP Support/Non-Revenue"
    
        #for filename in nonrevenue_files_clean:
        #    merger2.append(PdfReader(os.path.join(files_dir, filename), "rb"))
    
        for filename in nonrevenue_files_clean:
            if filename not in bobj_pdfs_merge:
                source_path = files_dir+'/'+ filename
            elif filename in bobj_pdfs_merge:
                source_path = bobj_dir+'/'+ filename
            log_step("MergePdfs", f"START: append Non-Revenue input {source_path}")
            merger2.append(source_path)
            log_step("MergePdfs", f"END: append Non-Revenue input {source_path}")
    
        pdf_name = "Executive Morning Package - Non-Revenue Core - "
        pdf_name_final = pdf_name + currentMonth + " " + currentDay + ", " + currentYear + ".pdf"
    
        write_merger_atomically(
            merger2, os.path.join(nonrevenue_output_dir, pdf_name_final), "MergePdfs"
        )
    
        nonrevenue_final_pdf = os.path.join(nonrevenue_output_dir, pdf_name_final)

        # To provide write permission to the file name- 09/01/2023 6:00 AM, change made by Z8182
        # Based on the CR - CHG0038130

        os.chmod(nonrevenue_final_pdf, stat.S_IRWXU)
        time.sleep(5)
    
        nonrevenue_merged_file = createPageNumbers(nonrevenue_output_dir,nonrevenue_final_pdf)
    
        scalePages(nonrevenue_merged_file, pdf_name_final)
        log_step("MergePdfs", "END: Non-Revenue Core report")
    
        #tkMessageBox.showinfo("Merge Files Completed", "Non Revenue Morning Package - Merge Successful")
        
        ####Non-Revenue ECM Morning Package merge files
    # =============================================================================
    #     merger3 = PdfMerger()
    #     nonrevenueECM_list = open(nonrevenueECM_pdfs).readlines()
    #     nonrevenueECM_list1 = [(nonrevECM.strip()) for nonrevECM in nonrevenueECM_list]
    #     nonrevenueECM_files = [i for e in nonrevenueECM_list1 for i in pdf_files if e in i]
    #     nonrevenueECM_files.sort()
    #     nonrevenueECM_files_clean = []
    #     [nonrevenueECM_files_clean.append(x) for x in nonrevenueECM_files if x not in nonrevenueECM_files_clean]  # remove duplicates
    # 
    #     nonrevenueECM_output_dir = "//TJAX2008FS/Entshare/Performance Measurements/Executive Morning Package/EMP Support/Non-Revenue"
    #     
    #     for filename in nonrevenueECM_files_clean:
    #         if filename not in bobj_pdfs_merge:
    #             merger3.append(PdfReader(os.path.join(files_dir, filename), "rb"))
    #         elif filename in bobj_pdfs_merge:
    #             merger3.append(PdfReader(os.path.join(bobj_dir, filename), "rb"))
    # 
    #     pdf_name = "Executive Morning Package - Non-Revenue - "
    #     pdf_name_final = pdf_name + currentMonth + " " + currentDay + ", " + currentYear + ".pdf"
    # 
    #     merger3.write(os.path.join(nonrevenueECM_output_dir, pdf_name_final))
    # 
    #     nonrevenueECM_final_pdf = os.path.join(nonrevenue_output_dir, pdf_name_final)
    # 
    #     nonrevenueECM_merged_file = createPageNumbers(nonrevenueECM_output_dir,nonrevenueECM_final_pdf)
    # 
    #     scalePages(nonrevenueECM_merged_file, pdf_name_final)
    # =============================================================================
    
        #tkMessageBox.showinfo("Merge Files Completed", "Non Revenue Morning Package for ECM - Merge Successful")
    
        if not time_list:
             
            with open("//TJAX2008FS/Entshare/Performance Measurements/Executive Morning Package/EMP Support/ExecutePython/logs/EMPMergeSuccess.txt",
                "a") as text_file:
                 text_file.write("All EMP Reports merged successfuly. " + str(today_ts) + "\n")
            
            msg['Subject'] = "EMP Automation: Reports Validation and Merge - Completed Successfully"
            body = "Reports have been merged successfully into their respective folders. \n\nPlease check the merged reports in folder: 'TJAX2008fs\\Entshare\\Performance Measurements\\Executive Morning Package\\EMP Support\\Daily Files'."
            msg.attach(MIMEText(body, 'plain'))
            text = msg.as_string()
            log_step("MergePdfs", "START: send merge-complete notification")
            send_graph_email(msg, toaddr + cc)
            log_step("MergePdfs", "END: merge-complete notification sent")
            log_step("MergePdfs", "START: run RegionalScorecard")
            regionalScorecard()
            log_step("MergePdfs", "END: RegionalScorecard import returned")
            
        elif time_list:
               
            with open("//TJAX2008FS/Entshare/Performance Measurements/Executive Morning Package/EMP Support/ExecutePython/logs/EMPMergeSuccess.txt",
                "a") as text_file:
                text_file.write("All EMP Reports merged successfuly. " + str(today_ts) + "\n")
                
            msg['Subject'] = "EMPAutomation: Reports Merge - Completed using file(s) from BOBJ folder. Daily Files Folder - Found OLD Reports"
            body = "Reports have been merged successfully into their respective folders. \n\nPlease check the merged reports in folder: 'TJAX2008fs\\Entshare\\Performance Measurements\\Executive Morning Package\\EMP Support\\Daily Files'." \
                    "\n\nFYI - There are OLD reports in Daily Files Folder. Please check if they are any OPEN files which may have caused BOBJ schedule to fail. "
            msg.attach(MIMEText(body, 'plain'))
            text = msg.as_string()
            log_step("MergePdfs", "START: send old-reports merge notification")
            send_graph_email(msg, toaddr + cc)
            log_step("MergePdfs", "END: old-reports merge notification sent")
            log_step("MergePdfs", "START: run RegionalScorecard")
            regionalScorecard()
            log_step("MergePdfs", "END: RegionalScorecard import returned")
            
            #Archive Cover Page for next days run
    #        cover_path = "//TJAX2008FS/Entshare/Performance Measurements/Executive Morning Package/EMP Support/Daily Files"
    #        archive_path = "//TJAX2008FS/Entshare/Performance Measurements/Executive Morning Package/EMP Support/Daily Files/Archive"
    #        pdf = [f for f in os.listdir(cover_path) if f.endswith("pdf") and "00" in f]
    #        cover_name = ''.join(pdf)
    #
    #        shutil.move(os.path.join(cover_path, cover_name),os.path.join(archive_path, cover_name))
    
        #Copy Non-Revenue report to Network Operations folder
        #from shutil import copyfile
        #dst_dir = "//TJAX2008FS/Entshare/Network Operations/Executive Morning Package"
        #copyfile(nonrevenue_merged_file, os.path.join(dst_dir, pdf_name_final))
        
    
    #Alert users if daily_files_missing has values (means that reports are missing in daily files folder but present in filedefinitions.txt)
    elif daily_files_missing_list:
        #message box
        #root = Tkinter.Tk()
        #root.withdraw()
        #tkMessageBox.showerror("Error - Missing Reports in Daily Files folder", "EMP Reports Validation Check \n\nMissing Reports in Daily Files folder but specified in filedefinitions.txt : \n\n"
        #                       + '\n'.join(str(x) for x in daily_files_missing_list))
        #email
        msg['Subject'] = "EMP Automation : Reports Validation Check Failed - Missing Reports"
        body = "There are missing reports in the Daily Files folder, but specified in file 'filedefinitions.txt' (in ExecutePython folder). Please contact BIG_Support (Big_Support@csx.com) for more information \n\nPlease check the listed reports below in folder: 'TJAX2008fs\\Entshare\\Performance Measurements\\Executive Morning Package\\EMP Support\\Daily Files' to make sure they are available. \n\n" \
               + '\n'.join(str(x) for x in daily_files_missing_list)
        msg.attach(MIMEText(body, 'plain'))
        text = msg.as_string()
        log_step("MergePdfs", "START: send missing-daily-reports notification")
        send_graph_email(msg, toaddr + cc)
        log_step("MergePdfs", "END: missing-daily-reports notification sent")
    
    #Alert users if the definition file doesn't have all the reports specified that daily files folder has.
    elif mapping_file_missing_list:
        # message box
        #root = Tkinter.Tk()
        #root.withdraw()
        #tkMessageBox.showerror("Error - FileDefinitions.txt does not have all the reports specified",
        #                     "EMP Reports Validation Check \n\nPlease add the missing report name(s) to 'filedefinitions.txt' (in ExecutePython folder) which are part of the EMP package : \n\n"
        #                     + '\n'.join(str(x) for x in mapping_file_missing_list))
        # email
        msg['Subject'] = "EMP Automation: Reports Validation Check Failed - FileDefinitions.txt does not have all the report names"
        body = "Report name(s) is missing in text file 'filedefinitions.txt' ! Please add the report name(s) to the file in ExecutePython folder. \n\n" + '\n'.join(
            str(x) for x in mapping_file_missing_list)
        msg.attach(MIMEText(body, 'plain'))
        text = msg.as_string()
        log_step("MergePdfs", "START: send mapping-file notification")
        send_graph_email(msg, toaddr + cc)
        log_step("MergePdfs", "END: mapping-file notification sent")
        
    log_step("MergePdfs", "END: EMP report merge workflow")
except KeyboardInterrupt:
    log_step("MergePdfs", "INTERRUPTED: merge stopped by user\n" + traceback.format_exc())
    raise
except Exception as e:
    log_step("MergePdfs", f"ERROR: {type(e).__name__}: {e}\n{traceback.format_exc()}")
    servicenow_details = {}
    servicenow_details['File Name'] = os.path.basename(sys.argv[0])
    print(e)
    print(traceback.print_exc())
    servicenow_message = 'EMP - Python Coding Error'
    servicenow_description = str(e) + '\n\n'
    servicenow_description = servicenow_description + traceback.format_exc()
    servicenow_send_alert(servicenow_message, servicenow_description, servicenow_details)
    raise
