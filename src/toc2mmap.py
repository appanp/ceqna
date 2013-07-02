#!/usr/bin/python
#
# Process the text file generated from pdftotext output of TOC PDF file
# USAGE: toc2mmap <i/p txt file from output of pdftotext> <o/p type: txt|mm>
# 
# NOTE:
import sys
import re

# START: Global variables 
rt_col_lines = []
curr_lt_topic = ''
curr_rt_topic = ''
cols = []
# END: Global variables

# START: Functions
def op_lt_col_txt(idx) :
    global curr_lt_topic, cols
    initNumRe = re.compile('^(\d+\.|\d+\.\d+|\d+\.\d+\.\d+)\s')
	# match() matches from the start while search() searches for pattern in entire string
    # Since using match() we could remove the ^ in the pattern as well.
    initNum = initNumRe.match(cols[idx].strip())
    if curr_lt_topic != '' :
        if not initNum :
			print curr_lt_topic + ' ' + cols[idx].strip() + ':' + cols[idx+1].strip()
        else :
			print curr_lt_topic
			print cols[idx].strip() + ':' + cols[idx+1].strip()
       	curr_lt_topic = ''
    else :
        print cols[idx].strip() + ':' + cols[idx+1].strip()

def op_lt_col_mm(idx) :
	global curr_lt_topic, cols
    initNumRe = re.compile('^(\d+\.|\d+\.\d+|\d+\.\d+\.\d+)\s')
	# match() matches from the start while search() searches for pattern in entire string
    # Since using match() we could remove the ^ in the pattern as well.
    initNum = initNumRe.match(cols[idx].strip())
    if curr_lt_topic != '' :
        if not initNum :
			print curr_lt_topic + ' ' + cols[idx].strip() + ':' + cols[idx+1].strip()
        else :
			print curr_lt_topic
			print cols[idx].strip() + ':' + cols[idx+1].strip()
       	curr_lt_topic = ''
    else :
        print cols[idx].strip() + ':' + cols[idx+1].strip()

def append_rt_col_lines(idx) :
    global curr_rt_topic, cols
    initNumRe = re.compile('^(\d+\.|\d+\.\d+|\d+\.\d+\.\d+)\s')
    initNum = initNumRe.match(cols[idx].strip())
    if curr_rt_topic != '':
        if not initNum :
        	rt_col_lines.append(curr_rt_topic + ' ' + cols[idx].strip() + ':' + cols[idx+1].strip())
        else :
			rt_col_lines.append(curr_rt_topic)
			rt_col_lines.append(cols[idx].strip() + ':' + cols[idx+1].strip())
        curr_rt_topic = ''
    else :
        rt_col_lines.append(cols[idx].strip() + ':' + cols[idx+1].strip())

def add_curr_lt_topic(idx) :
    global curr_lt_topic, cols
    if curr_lt_topic != '':
        curr_lt_topic += ' ' + cols[idx].strip()
    else :
        curr_lt_topic = cols[idx].strip()

def add_curr_rt_topic(idx) :
    global curr_rt_topic, cols
    if curr_rt_topic != '':
        curr_rt_topic += ' ' + cols[idx].strip()
    else :
        curr_rt_topic = cols[idx].strip()

def op_rt_col_lines_txt() :


def op_rt_col_lines_mm() :

# END: Functions

# START: Main
if (len(sys.argv) != 3):
  print >>sys.stderr,"Usage: "+__file__+" <pdftotext o/p txt file> <mm or txt>"
  sys.exit(-1)
ipF = open(sys.argv[1],'r')
opTyp = sys.argv[2]
for line in ipF :
  # Assuming 52-58 as column range for left column page number occurrence
  discard = re.compile('^\s*$|\s+(Contents|CONTENTS|PROOF|Proof)\s*')
  line_to_discard = discard.search(line)
  if not line_to_discard:
    # find might be faster - not sure
    pg = re.search('\s+Page\s+',line)
    if pg :
	    #print "*** Page end found, len or right col:",len(rt_col_lines)
	    for itm in rt_col_lines:
		    print itm
	    rt_col_lines = []
	    continue
    # List of possibilities with split array length for each one:
    # <lt col>                     : 1,
    #                <rt col>      : 1,
    # <lt col>       <rt col>      : 1,
    # <lt col> <num>               : 4, col[3] is empty string
    #                <rt col> <num>: 4. col[3] is empty string
    # <lt col>       <rt col> <num>: 4, col[3] is empty string
    # <lt col> <num> <rt col>      : 4, col[3] is <rt col>
    # <lt col> <num> <rt col> <num>: 7, col[6] is empty string
    p = re.compile('\s\s+([ixv]+|\d+)(\s+|$)')
    l_spcs = re.compile('\s+')
    l_spcs_mo = l_spcs.match(line)
    cols = p.split(line)
    #print "...len of cols:"+str(len(cols))+" line:"+line
    if len(cols) == 1 :
		# Could be either left and/or right column without page number
        if l_spcs_mo and (l_spcs_mo.end() >= 60) :
            add_curr_rt_topic(0)
        else :
            add_curr_lt_topic(0)
        # TODO: Handle both left & right cols. texts
    elif len(cols) == 2 or len(cols) == 3 :
        # This can never happen: just print the line
        print "...Split array has two/three segments"
    elif len(cols) == 4 :
        if cols[3].strip() != '' :
            if opTyp == 'mm' :
	            op_lt_col_mm(0)
            else :
			    op_lt_col_txt(0)
            add_curr_rt_topic(3)
        else :
            if l_spcs_mo and (l_spcs_mo.end() >= 60) :
                append_rt_col_lines(0)
            else :
                idx_num = line.find(cols[1])
                if idx_num != -1 and idx_num < 60 :
                    #TODO: Add filtering of string before printing
                    if opTyp == 'mm' :
	                    op_lt_col_mm(0)
                    else :
			            op_lt_col_txt(0)
                else :
                    # Split cols[0] with more than 3 spaces & store left col & append right col
                    spc_idx = l_spcs_mo.end()
                    if curr_lt_topic != '' :
                    	curr_lt_topic += ' ' + cols[0][spc_idx:59].strip()
                    else :
						curr_lt_topic = cols[0][spc_idx:59].strip()
                    rt_col_str = cols[0][60:].strip()
                    if curr_rt_topic != '':
                        rt_col_lines.append(curr_rt_topic + ' ' + rt_col_str + ':' + cols[1].strip())
                        curr_rt_topic = ''
                    else :
                        rt_col_lines.append(rt_col_str + ':' + cols[1].strip())
    elif len(cols) == 5 or len(cols) == 6 :
        # This can never happen: just print the line
        print "...Split array has five/six segments"
    elif len(cols) == 7 :
#TODO: Add filtering of string before printing
        if opTyp == 'mm' :
	        op_lt_col_mm(0)
        else :
            op_lt_col_txt(0)
        append_rt_col_lines(3)
    else :
        print "...Length of split string with num more than 5:"
        for col in cols:
            print "......",col
        print "...End of Cols"
if len(rt_col_lines) != 0:
    for itm in rt_col_lines:
        print itm
    rt_col_lines = []
                 
