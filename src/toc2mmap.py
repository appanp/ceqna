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
last_depth = 0
node_id = 1
part_present = 0
debug = 0
# END: Global variables

# START: Functions
def get_depth(ip_str) :
    global part_present
    dep = 0
    spc = ip_str.find(' ')
    num_pfx = ip_str[0:spc]
    if ip_str.startswith('PART'):
        dep = 1
        part_present = 1
    else:
        num_dots = num_pfx.count('.')
        if num_pfx.strip().endswith('.') :
            dep = num_dots + 1
        else :
            if part_present :
			    dep = num_dots + 2
            else :
				dep = num_dots + 1
    #print >>sys.stderr,"*** get_depth() ip_str:"+ip_str+" dep:"+str(dep)
    return dep

def op_end_tags(dep) :
    global last_depth
    # if last_depth - dep < 0, no need to do anything
    if last_depth == dep :
        print '</node>' # End tag for the prev. node
    elif last_depth == (dep + 1) :
        print '</node>' # End tag for the prev. node
        print '</node>' # End tag dor prev. containing node
    elif last_depth == (dep + 2) :
        print '</node>' # End tag for the prev. node
        print '</node>' # End tag dor prev. containing node
        print '</node>'
    elif last_depth == (dep + 3) :
        print '</node>' # End tag for the prev. node
        print '</node>' # End tag dor prev. containing node
        print '</node>' # End tag dor prev. containing node
        print '</node>'
    else :
        if last_depth - dep > 3 :
            print >>sys.stderr,"last_depth - dep > 3, not handled: " + str(last_depth) + ' - ' + str(dep)
    last_depth = dep

def op_lt_col_txt(idx) :
    global curr_lt_topic, cols
    initNumRe = re.compile('^(?P<sect_num>\d+\.?|\d+\.\d+|\d+\.\d+\.\d+)\s')
	# match() matches from the start while search() searches for pattern in entire string
    # Since using match() we could remove the ^ in the pattern as well.
    initNum = initNumRe.match(cols[idx].strip())
    if curr_lt_topic != '' :
        if not initNum :
			print curr_lt_topic + ' ' + ' '.join(cols[idx].strip().split()) + ':' + cols[idx+1].strip()
        else :
			print curr_lt_topic
			print ' '.join(cols[idx].strip().split()) + ':' + cols[idx+1].strip()
       	curr_lt_topic = ''
    else :
        print ' '.join(cols[idx].strip().split()) + ':' + cols[idx+1].strip()

def op_lt_col_mm(idx) :
    global curr_lt_topic, cols, node_id
    initNumRe = re.compile('^(?P<sect_num>\d+\.?|\d+\.\d+|\d+\.\d+\.\d+)\s')
    # match() matches from the start while search() searches for pattern in entire string
    # Since using match() we could remove the ^ in the pattern as well.
    initNum = initNumRe.match(cols[idx].strip())
    if curr_lt_topic != '' :
        if not initNum :
            dep = get_depth(curr_lt_topic)
            op_end_tags(dep)
            if debug:
                nodeTxt = curr_lt_topic + ' ' + ' '.join(cols[idx].strip().split()) + ':' + cols[idx+1].strip() + ':' + str(dep)
            else:
                nodeTxt = curr_lt_topic + ' ' + ' '.join(cols[idx].strip().split()) + ':' + cols[idx+1].strip()
            print '<node CREATED="1347382439772" ID="ID_'+str(node_id)+'" MODIFIED="1347382510988" TEXT="'+nodeTxt.encode('utf-8')+'">'
            node_id = node_id + 1
        else :
            dep = get_depth(curr_lt_topic)
            op_end_tags(dep)
            if debug:
                nodeTxt = curr_lt_topic + ':' + str(dep)
            else:
                nodeTxt = curr_lt_topic
            print '<node CREATED="1347382439772" ID="ID_'+str(node_id)+'" MODIFIED="1347382510988" TEXT="'+nodeTxt.encode('utf-8')+'">'
            node_id = node_id + 1
            section_num = initNum.group('sect_num')
            dep = get_depth(section_num)
            op_end_tags(dep)
            if debug:
                nodeTxt = ' '.join(cols[idx].strip().split()) + ':' + cols[idx+1].strip() + ':' + str(dep)
            else :
                nodeTxt = ' '.join(cols[idx].strip().split()) + ':' + cols[idx+1].strip()
            print '<node CREATED="1347382439772" ID="ID_'+str(node_id)+'" MODIFIED="1347382510988" TEXT="'+nodeTxt.encode('utf-8')+'">'
            node_id = node_id + 1
       	curr_lt_topic = ''
    else :
        initNumRe = re.compile('(PART|\d+\.?|\d+\.\d+|\d+\.\d+\.\d+)\s')
        initNum = initNumRe.match(cols[idx].strip())
        if initNum is not None :
            dep = get_depth(cols[idx].strip())
            op_end_tags(dep)
            if debug:
                nodeTxt = ' '.join(cols[idx].strip().split()) + ':' + cols[idx+1].strip() + ':' + str(dep)
            else:
                nodeTxt = ' '.join(cols[idx].strip().split()) + ':' + cols[idx+1].strip()
            print '<node CREATED="1347382439772" ID="ID_3_'+str(node_id)+'" MODIFIED="1347382510988" TEXT="'+nodeTxt.encode('utf-8')+'">'
            node_id = node_id + 1
        else:
            # Take care of case when it is PART<spc><Num> which is taken as page num
            if cols[idx].strip().startswith('PART') :
                curr_lt_topic = cols[idx].strip() + ' ' +cols[idx+1].strip()

def append_rt_col_lines(idx) :
    global rt_col_lines, curr_rt_topic, cols
    #print >>sys.stderr,"+++ In append_rt_col_lines:"+cols[idx].strip()+':'+cols[idx+1].strip()
    initNumRe = re.compile('(\d+\.?|\d+\.\d+|\d+\.\d+\.\d+)\s')
    initNum = initNumRe.match(cols[idx].strip())
    if curr_rt_topic != '':
        if not initNum :
            rt_col_lines.append(curr_rt_topic + ' ' + cols[idx].strip() + ':' + cols[idx+1].strip())
        else :
            rt_col_lines.append(curr_rt_topic)
            rt_col_lines.append(cols[idx].strip() + ':' + cols[idx+1].strip())
        curr_rt_topic = ''
    else :
        if cols[idx].strip().startswith('PART') :
            curr_rt_topic = cols[idx].strip() + ' ' + cols[idx+1].strip()
        else :
            rt_col_lines.append(cols[idx].strip() + ':' + cols[idx+1].strip())

def add_curr_lt_topic(idx) :
    global curr_lt_topic, cols
    if curr_lt_topic != '':
        curr_lt_topic += ' ' + ' '.join(cols[idx].strip().split())
    else :
        curr_lt_topic = ' '.join(cols[idx].strip().split())

def add_curr_rt_topic(idx) :
    global curr_rt_topic, cols
    if curr_rt_topic != '':
        curr_rt_topic += ' ' + cols[idx].strip()
    else :
        curr_rt_topic = cols[idx].strip()

def op_rt_col_lines_txt() :
    global rt_col_lines
    for itm in rt_col_lines:
		print itm
    rt_col_lines = []

def op_rt_col_lines_mm() :
    global rt_col_lines, node_id
    initNumRe = re.compile('(PART|\d+\.?|\d+\.\d+|\d+\.\d+\.\d+)\s')
    for itm in rt_col_lines:
        initNum = initNumRe.match(itm)
        if initNum is not None :
            dep = get_depth(itm)
            op_end_tags(dep)
            if debug:
                nodeTxt = itm + ':' + str(dep)
            else :
                nodeTxt = itm
            print '<node CREATED="1347382439772" ID="ID_'+str(node_id)+'" MODIFIED="1347382510988" TEXT="'+nodeTxt.encode('utf-8')+'">'
            node_id = node_id + 1
    rt_col_lines = []

# Function to determine if the i/p line is to be discarded
def chk_for_discard(line):
  retval = False
  # Added this check for NCERT books which have watermark
  n_line = ' '.join(line.split())
  # TODO: We need more robust logic to deduct watermarks spread across lines
  # Currenly num 10 below is magic !! 
  if len(n_line) <= 10:
    retval = True
  else:
    discard = re.compile('^\s*$|\s+(Contents|CONTENTS|PROOF|Proof)\s*')
    line_to_discard = discard.search(line)
    if line_to_discard is not None:
	  retval = True
  return retval

# END: Functions

# START: Main
print >>sys.stderr,"...Num. of i/p args: "+str(len(sys.argv))
if (len(sys.argv) != 4):
  print >>sys.stderr,"Usage: "+__file__+" <pdftotext o/p txt file> <mm or txt> <root node text"
  sys.exit(-1)
ipF = open(sys.argv[1],'r')
opTyp = sys.argv[2]
root_txt = sys.argv[3]
if opTyp == 'mm' :
    # Print the header of the .mm XML file
    print '<map version="1.0.0">'

    # Print the first or root node
    print '<node CREATED="1347382439772" ID="ID_'+str(node_id)+'" LINK="'+sys.argv[1]+'" MODIFIED="1347382510988" TEXT="'+root_txt+'">'
    node_id = node_id + 1

for line in ipF :
  # Assuming 52-58 as column range for left column page number occurrence
  if not chk_for_discard(line):
    # find might be faster - not sure
    pg = re.search('\s+Page\s+',line)
    if pg :
	    #print "*** Page end found, len or right col:",len(rt_col_lines)
        if opTyp == 'mm' :
            op_rt_col_lines_mm()
        else :
            op_rt_col_lines_txt()
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
    #p = re.compile('\s\s+([ixv]+|\d+)(\s+|$)')
    p = re.compile('\s+([ixv]+|\d+)(\s+|$)')
    l_spcs = re.compile('^\s+')
    l_spcs_mo = l_spcs.match(line)
    cols = p.split(line)
    #print >>sys.stderr,"...len of cols:"+str(len(cols))+" line:"+line
    if len(cols) == 1 :
		# Could be either left and/or right column without page number
        if l_spcs_mo and (l_spcs_mo.end() >= 60) :
            add_curr_rt_topic(0)
        else :
            add_curr_lt_topic(0)
        # TODO: Handle both left & right cols. texts
    elif len(cols) == 2 or len(cols) == 3 :
        # This can never happen: just print the line
        print >>sys.stderr,"...Split array has two/three segments"
    elif len(cols) == 4 :
        if cols[3].strip() != '' :
            if opTyp == 'mm' :
	            op_lt_col_mm(0)
            else :
			    op_lt_col_txt(0)
            add_curr_rt_topic(3)
        else :
            #print >>sys.stderr, "...i/p line: "+line
            if l_spcs_mo and (l_spcs_mo.end() >= 60) :
                append_rt_col_lines(0)
            else :
                # The magic number 20 is for beginning of left col text after spaces 
                #idx_num = line.find(cols[1])
                idx_num = line.find(cols[0])
                if idx_num != -1 and idx_num < 25 :
                    #TODO: Add filtering of string before printing
                    if opTyp == 'mm' :
	                    op_lt_col_mm(0)
                    else :
			            op_lt_col_txt(0)
                else :
                    # Split cols[0] with more than 3 spaces & store left col & append right col
					# Giving error for NCERT books ToCs. 'coz of page watermarks. 
                    print >>sys.stderr,"......i/p line is:"+line
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
        print >>sys.stderr,"...Split array has five/six segments"
    elif len(cols) == 7 :
#TODO: Add filtering of string before printing
        if opTyp == 'mm' :
	        op_lt_col_mm(0)
        else :
            op_lt_col_txt(0)
        append_rt_col_lines(3)
    else :
        print >>sys.stderr,"...Length of split string with num more than 5:"
        for col in cols:
            print >>sys.stderr,"......",col
        print >>sys.stderr,"...End of Cols"
if len(rt_col_lines) != 0:
    if opTyp == 'mm' :
        op_rt_col_lines_mm()
    else :
        op_rt_col_lines_txt()
if opTyp == 'mm' :
    op_end_tags(1)
    print '</node>'
    print '</map>'
