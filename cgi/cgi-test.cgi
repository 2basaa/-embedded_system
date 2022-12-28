#!/usr/bin/python

import cgi, cgitb
cgitb.enable()

form = cgi.FieldStorage()

print("Content-Type: text/html\n")
print("<html><body>\n")
print("<h3>Python CGI test</h3>")

for var in form.keys():
        val = form[var].value
        print("%s = %s<br> " % (var,val))

print("</body></html>\n")