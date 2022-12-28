#!/usr/bin/python

import cgi,cgitb
cgitb.enable()
import random

x = random.randint(1,100)
y = random.randint(1,100)
z = random.randint(1,100)

print("Content-Type: text/xml\n")
print("<?xml version=\"1.0\" encoding=\"UTF-8\"?>")
print("<data>\n<x>%s</x>\n<y>%s</y>\n<z>%s</z>\n</data>" % (x,y,z))