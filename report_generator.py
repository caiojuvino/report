# coding: UTF-8
# Report Generator
# Author: Laercio Vitorino
# Review: Denys Lins, Caio Juvino
# Date: 06/08/2015

# The script below is aimed to help the Q&A team to generate reports of
# app feedback in an automated fashion.

# The libray Naked is necessary to run a node.js script

import codecs, csv, datetime, matplotlib, os, sys, time
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from Naked.toolshed.shell import execute_js
from reportlab.lib.colors import black, red, white, green
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader, simpleSplit
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Image, Paragraph

# This function converts the csv file to utf-8 encoding
def convert_to_utf8(sourceFileName):
    # desired size in bytes
    BLOCKSIZE = 1048576
    targetFileName = sourceFileName[:-4] + "_2.csv"
    
    try:
        with codecs.open(sourceFileName, "r", "utf-16") as sourceFile:
            with codecs.open(targetFileName, "w", "utf-8") as targetFile:
                while True:
                    contents = sourceFile.read(BLOCKSIZE)
                    if not contents:
                        break
                    targetFile.write(contents)

        os.remove(sourceFileName)
        os.rename(targetFileName, sourceFileName)
    
    except UnicodeError:
        os.remove(targetFileName)
        print "CSV file \"%s\" is already utf-8 encoded." %sourceFileName

# This function creates the page header of reports
def create_page_header(text, font_size=14, color=white, data=""):
    image = ImageReader("embedded.jpg")
    pdf_file.drawImage(image, 0 * mm, 265 * mm, 210 * mm, 23 * mm, preserveAspectRatio=True)
    pdf_file.setFillColor(color, 1)
    pdf_file.setFont("Helvetica-Bold", font_size)
    pdf_file.drawString(10 * mm, 280 * mm, text.upper())
    pdf_file.drawString(10 * mm, 270 * mm, data.upper())


def format_date(date):
    date = date.split("-")[::-1]
    return "%s/%s/%s" %(date[0], date[1], date[2])

# This function inserts a line in the pdf file
def insert_line(text, margin=0, size=12, color=black):
    global ACTUAL_LINE
    s = ParagraphStyle('my_style')
    s.textColor = color
    s.fontSize = size
    s.fontName = "Helvetica"
    s.leftIndent = margin
    lines = simpleSplit(text, "Helvetica", size, aW - 25 * mm)
    for line in lines:
        p = Paragraph(line, s)
        p.wrapOn(pdf_file, aW, aH)
        p.drawOn(pdf_file, 10 * mm, ACTUAL_LINE * mm)
        ACTUAL_LINE -= 9

# This function sets the csv file to be read
def set_csv_filename(project_name, view):
    return "installs_org.embeddedlab.%s/installs_org.embeddedlab.%s_201508_%s.csv" %(project_name, project_name, view)

# This function recovers the latest rows of csv file 
def get_latest_rows(filereader):
    day = '00'
    lines = []
    
    for line in filereader:
        if line[0][-2:] > day:
            day = line[0][-2:]
            lines = []
        lines.append(line)
    return lines

# This function checks if there is sapce left to write into pdf file
def check_new_page():
    global ACTUAL_LINE
    if ACTUAL_LINE <= 35:
        ACTUAL_LINE = 250
        pdf_file.showPage()
        create_page_header(proj_name, 13, white, date)

PAGE_WIDTH, PAGE_HEIGHT = A4
aW = PAGE_WIDTH
aH = PAGE_HEIGHT

if len(sys.argv) != 2:
    print("Missing args: project name")
    print("Use: python report_generator <project_name>")
    sys.exit(1)

pdf_file = Canvas("Report_" + sys.argv[1] + time.strftime("%d-%m-%Y_%H-%M-%S") + ".pdf")
csv_file_name = set_csv_filename(sys.argv[1], "overview")
convert_to_utf8(csv_file_name)
date = time.strftime("%d-%m-%Y")
ACTUAL_LINE = 250

with open(csv_file_name, 'rb') as weeklyreport:    
    filereader = csv.reader(weeklyreport, delimiter=',', quotechar='"')
    first_line = filereader.next()
    
    days = 0
    lines = []
    dates = []
    #Jumps to last line
    for line in filereader:
        lines.append(line[2])
        dates.append(line[0])
        days +=1

    last_line = line
    proj_name = last_line[1][16:]
    create_page_header(proj_name, 13, white, date)
    
    insert_line("Installs Overview", 0, 16)

    for i in range (2,10):
        insert_line(first_line[i] + ": " + last_line[i], 20)

#-----------------------------------------------------------------------
    lines = map(int,lines)
    larger = max(lines)
    smaller = min(lines)
    gap = larger - smaller

    frame = plt.gca()
    for xlabel_i in frame.axes.get_xticklabels():
        xlabel_i.set_visible(False)

    plt.ylabel('Current Installs')
    plt.xlabel(format_date(dates[0]) + " to " + format_date(dates[-1]))
    plt.plot(range(days), lines, 'g-')
    plt.axis([0, days - 1, smaller - gap, larger])
    
    image_name = proj_name + ".png"
    plt.savefig(image_name)
    image = ImageReader(image_name)
    pdf_file.drawImage(image, 90 * mm, 170 * mm, 110 * mm, 80 * mm)
#-----------------------------------------------------------------------

csv_file_name = set_csv_filename(sys.argv[1], "os_version")
convert_to_utf8(csv_file_name)

with open(csv_file_name, 'rb') as weeklyreport:
    filereader = csv.reader(weeklyreport, delimiter=',', quotechar='"')
    first_line = filereader.next()
    
    lines = get_latest_rows(filereader)
    insert_line("Installs by Android Version", 0, 16)
    
    for line in lines:
        insert_line(line[2], 20)
        for i in range (3,10):
            insert_line(first_line[i] + ": " + line[i], 40)
        check_new_page()

csv_file_name = set_csv_filename(sys.argv[1], "device")
convert_to_utf8(csv_file_name)

with open(csv_file_name, 'rb') as weeklyreport:
    filereader = csv.reader(weeklyreport, delimiter=',', quotechar='"')
    first_line = filereader.next()
    
    lines = get_latest_rows(filereader) 
    insert_line("Installs by Device", 0, 16)
    
    for line in lines:
        insert_line(line[2], 20)
        for i in range (3,10):
            insert_line(first_line[i] + ": " + line[i], 40)
        check_new_page()

csv_file_name = set_csv_filename(sys.argv[1], "country")
convert_to_utf8(csv_file_name)

with open(csv_file_name, 'rb') as weeklyreport:
    filereader = csv.reader(weeklyreport, delimiter=',', quotechar='"')
    first_line = filereader.next()
    
    lines = get_latest_rows(filereader) 
    insert_line("Installs by Country", 0, 16)
    
    for line in lines:
        insert_line(line[2], 20)
        for i in range (3,10):
            insert_line(first_line[i] + ": " + line[i], 40)
        check_new_page()

csv_file_name = set_csv_filename(sys.argv[1], "language")
convert_to_utf8(csv_file_name)

with open(csv_file_name, 'rb') as weeklyreport:
    filereader = csv.reader(weeklyreport, delimiter=',', quotechar='"')
    first_line = filereader.next()
    
    lines = get_latest_rows(filereader) 
    insert_line("Installs by Language", 0, 16)
    
    for line in lines:
        insert_line(line[2], 20)
        for i in range (3,10):
            insert_line(first_line[i] + ": " + line[i], 40)
        check_new_page()

csv_file_name = set_csv_filename(sys.argv[1], "app_version")
convert_to_utf8(csv_file_name)

with open(csv_file_name, 'rb') as weeklyreport:
    filereader = csv.reader(weeklyreport, delimiter=',', quotechar='"')
    first_line = filereader.next()
    
    lines = get_latest_rows(filereader) 
    insert_line("Installs by Version", 0, 16)
    
    for line in lines:
        insert_line("App Version: %s" %line[2], 20)
        for i in range (3,10):
            insert_line(first_line[i] + ": " + line[i], 40)
        check_new_page()

csv_file_name = set_csv_filename(sys.argv[1], "tablets")
convert_to_utf8(csv_file_name)

with open(csv_file_name, 'rb') as weeklyreport:
    filereader = csv.reader(weeklyreport, delimiter=',', quotechar='"')
    first_line = filereader.next()
    
    lines = get_latest_rows(filereader) 
    insert_line("Installs by Tablets", 0, 16)
    
    for line in lines:
        insert_line(line[2].replace("_", " "), 20)
        for i in range (3,10):
            insert_line(first_line[i] + ": " + line[i], 40)
        check_new_page()

pdf_file.save()
