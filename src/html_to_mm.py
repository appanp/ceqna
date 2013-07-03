#!/usr/bin/python
#
# Script to convert Table-of-Contents of a book into mindmap .mm file
# INPUTS:
# 1. URL or local HTML file containing the ToC
#
# CAUTION:
# This script is written for a ToC file such as PLP 3e TOC:
# http://www.cs.rochester.edu/u/scott/pragmatics/3e/toc.shtml
#
# Other 'templates of HTML' that can be handled is one of embedded HTML lists
# http://www.computer.org/portal/web/publications/acmtaxonomy
# 
# nother organization of a hierarchy of terms is a set of hierarchical web pages
# with a root such as this ACM Comput. Classification Systems page:
# http://dl.acm.org/ccs.cfm

import sys
import os
from lxml.html.clean import clean_html
from pyquery import PyQuery
import subprocess

def prn_mm_for_sec(index, node) :
  global last_rowTxt,node_id, curr_dep, last_dep, depth
  ce = PyQuery(node)
  rowTxt = ce.text()
  cols = ce('td')
  curr_dep = len(cols)

  # First close the previous node if required
  #if curr_dep == 1 and cols[0].text() == '' :
  if curr_dep == 1 :
       # This is a blank line which ends a section or sub-sec
       print >>sys.stderr,"...Blank line: End of NODE, depth="+str(depth)
       print >>sys.stderr,"......Last Row Text:"+last_rowTxt
       for i in range (0,depth) :
           print '</node>'
       depth=0
  elif curr_dep == (last_dep + 1) :
    # This means a new nesting starts, just inc. depth
    depth = depth + 1
    if index == 0 :
        print >>sys.stderr,"...Start of new level-2 node: "+rowTxt
  elif (curr_dep + 1) == last_dep :
    # This means a nesting has ended, dec. depth & print 2 end tags
    depth = depth - 1
    print '</node>'
    print '</node>'
  elif curr_dep  == last_dep :
    # This means are at the same level: just end the previous node tag
    print '</node>'
  elif curr_dep >= 3 and  last_dep == 1 :
    # This means start of a new level-1 node
    # DO NOTHING
    print >>sys.stderr,"...Start of new level-2 node: "+rowTxt
    depth = 1
  else :
    print >>sys.stderr,"...Curr dep. is neither one more or less than prev. depth"
    print >>sys.stderr,"......Curr. dep:"+str(curr_dep)+" last dep:"+str(last_dep)
    print >>sys.stderr,"......Last Row Text:"+last_rowTxt
    print >>sys.stderr,"......Curr. Row Text:"+rowTxt
  # Next print the text for current node if not empty line
  if curr_dep >= 2 :
    nodeTxt = PyQuery(cols[curr_dep - 2]).text()+" "+PyQuery(cols[curr_dep - 1]).text()
    print '<node CREATED="1347382439772" ID="ID_'+str(node_id)+'" MODIFIED="1347382510988" TEXT="'+nodeTxt.encode('utf-8')+'">'
  last_dep = curr_dep
  last_rowTxt = rowTxt
  node_id = node_id + 1

def prn_tbl_sec(index, node) :
  global node_id, curr_dep, last_dep, depth
  if index != 0 :
    print >>sys.stderr,"...Start of PART, depth="+str(depth)
    ce = PyQuery(node)
    # Print the part heading as containing node
    partLst = ce.prevAll('h3')
    partTxt = PyQuery(partLst[len(partLst)-1]).text()
    if index % 2 == 0 :
        print '<node CREATED="1347382439772" ID="PartID_'+str(index)+'" POSITION="left" MODIFIED="1347382510988" TEXT="'+partTxt.encode('utf-8')+'">'
    else :
        print '<node CREATED="1347382439772" ID="PartID_'+str(index)+'" POSITION="right" MODIFIED="1347382510988" TEXT="'+partTxt.encode('utf-8')+'">'
    rows = ce('tr')
    rows.each(prn_mm_for_sec)
    # Print the closing tags for this table
    print >>sys.stderr,"...End of PART, depth="+str(depth)
    for i in range (0,depth) :
      print '</node>'
    print '</node>' #For the part heading containing node
    depth=0
    last_dep = 3

# START: of MAIN
last_rowTxt = ''
last_dep = 3
curr_dep = 0
node_id = 1
depth = 0

if (len(sys.argv)  == 1):
  print >>sys.stderr,"Usage: "+__file__+" <URL/HTML file>"
  sys.exit(-1)
ipUrl = sys.argv[1]
if ipUrl.find('http') == 0 :
  d = PyQuery(ipUrl)
else :
  html = open(ipUrl,'r').read()
  d = PyQuery(html)

# Print the header of the .mm XML file
print '<map version="1.0.0">'

# Print the first or root node
print '<node CREATED="1347382439772" ID="ID_'+str(node_id)+'" LINK="http://www.mkse.upenn.edu" MODIFIED="1347382510988" TEXT="PLP 3e">'
node_id = node_id + 1
#rows = d('body > table tr')
rows = d('table')
rows.each(prn_tbl_sec)

# Print the closing tags & other footer info
for i in range (0,depth+1) :
    print '</node>'
print '</map>'
