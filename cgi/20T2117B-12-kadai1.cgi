#!/usr/bin/python

import cgi, cgitb
import datetime

cgitb.enable()

form = cgi.FieldStorage()
real_time = datetime.datetime.now()
if "mode" not in form:#mode == True
    mode = real_time
elif str(form['mode'].value) == "date":
    mode = datetime.date.today()
elif str(form['mode'].value) == "time":#mode == False
    mode = real_time.time()

print("Content-Type: text/html\n")
print("<html><body>\n")
print("<h3>Python CGI test</h3>\n")
print("mode=%s" % mode)
print("</body></html>\n")