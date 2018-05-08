#!/usr/bin/python
from bs4 import BeautifulSoup
import mechanize
import re
from HTMLParser import HTMLParser
from itertools import izip
import paho.mqtt.publish as publish
class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

def match_class(target):
    target = target.split()
    def do_match(tag):
        classes = dict(tag.attrs).get('class', '')
        return all(c in classes for c in target)
    return do_match

def remove_attrs(soup):
    for tag in soup.findAll(True): 
        tag.attrs = None
    return soup

br = mechanize.Browser()
br.set_handle_robots(False)   # ignore robots
br.set_handle_refresh(False)  # can sometimes hang without this
br.addheaders = [('User-agent', 'Firefox')]

url = "http://classic.laundryview.com/laundry_room.php?lr=700807842"
response = br.open(url)

br.form = list(br.forms())[0]

for control in br.form.controls:
    if control.type == "select": pass # means it's class ClientForm.SelectControl
#       for item in control.items:
#	        print str([label.text.encode("utf-8")  for label in item.get_labels()]).encode("utf-8")

control.value = ["700807842"]

response = br.submit()
soup = BeautifulSoup(response.read(), 'html.parser')
#print soup
matches = soup.findAll(match_class("monitor-total"))
matches2 = soup.findAll('option')
#for x in matches2:
#    print x['value']
#    for y in x:
#        print y

#print zip(matches, matches2)
for x in  str(list(matches)[0]).split('<span class="monitor-types">WASHERS:</span> ', 1):
    if "available" in x:
        washers = str((x.split("\n")[0]))
        publish.single("/sparti/laundry/washers", "Washers: "+washers)

for x in  str(list(matches)[0]).split('<span class="monitor-types">DRYERS:</span> ', 1):
        publish.single("/sparti/laundry/dryers", "Dryers:"+ str(x.split("\n")[0].split('<div class="monitor-total">')[0]))
#        +dryers)
#for m,n in zip(matches, matches2):
#    print(str(m.read()).split("=")[1])#x,n)
#    if "DRYERS" in m:
#        print "DRYERS"
#        publish.single("/sparti/laundry/dryers_available", str(m).split("DRYERS",1)[1])
