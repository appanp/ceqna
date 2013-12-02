#!/usr/bin/python
#
# Process the text file generated from pdftotext output of TOC PDF file
# USAGE: toc2mmap <i/p txt file from output of pdftotext> <o/p type: txt|mm>
# 
# NOTE:
import sys
import re
import xml.parsers.expat

# START: Global variables 
rt_col_lines = []
curr_lt_topic = ''
curr_rt_topic = ''
cols = []
last_depth = 0
node_id = 1
part_present = 0
debug = 0
#debug = 0
# END: Global variables

# START: Functions
def parseXmlFile(file):
	parser = xml.parsers.expat.ParserCreate()
	parser.ParseFile(open(file,'r'))

def get_depth(ip_str) :
    global part_present
    dep = 0
    spc = ip_str.find(' ')
    num_pfx = ip_str[0:spc]
    if ip_str.startswith('PART') :
        dep = 1
        part_present = 1
    elif ip_str.startswith('CHAPTER') :
		dep = 1
    else:
        num_dots = num_pfx.count('.')
        if num_pfx.strip().endswith('.') :
            if num_dots == 1:
				dep = num_dots
            else :
				dep = num_dots + 1
        else :
            if part_present :
			    dep = num_dots + 2
            else :
				dep = num_dots + 1
    print >>sys.stderr,"*** get_depth() ip_str:"+ip_str+" dep:"+str(dep)
    return dep

def op_end_tags(dep) :
    global last_depth
    # if last_depth - dep < 0, no need to do anything
    if last_depth == dep :
        print >>opF,'</node>' # End tag for the prev. node
    elif last_depth == (dep + 1) :
        print >>opF,'</node>' # End tag for the prev. node
        print >>opF,'</node>' # End tag dor prev. containing node
    elif last_depth == (dep + 2) :
        print >>opF,'</node>' # End tag for the prev. node
        print >>opF,'</node>' # End tag dor prev. containing node
        print >>opF,'</node>'
    elif last_depth == (dep + 3) :
        print >>opF,'</node>' # End tag for the prev. node
        print >>opF,'</node>' # End tag dor prev. containing node
        print >>opF,'</node>' # End tag dor prev. containing node
        print >>opF,'</node>'
    else :
        if last_depth - dep > 3 :
            print >>sys.stderr,"last_depth - dep > 3, not handled: " + str(last_depth) + ' - ' + str(dep)
    last_depth = dep

def op_lt_col_txt(tpc,pg_num) :
    global curr_lt_topic
    initNumRe = re.compile('^(?P<sect_num>\d+\.?|\d+\.\d+|\d+\.\d+\.\d+)\s')
	# match() matches from the start while search() searches for pattern in entire string
    # Since using match() we could remove the ^ in the pattern as well.
    initNum = initNumRe.match(tpc.strip())
    if curr_lt_topic != '' :
        if not initNum :
			print >>opF,curr_lt_topic + ' ' + ' '.join(tpc.strip().split()) + ':' + pg_num.strip()
        else :
            section_num = initNum.group('sect_num')
            print >>opF,"--- section_num:"+section_num
            dep = get_depth(section_num)
            print >>opF,curr_lt_topic
            if dep == 1:
                print >>opF,' '.join(tpc.strip().split())
            else:
                print >>opF,' '.join(tpc.strip().split()) + ':' + pg_num.strip()
       	curr_lt_topic = ''
    else :
        if initNum:
            section_num = initNum.group('sect_num')
            print >>opF,"--- section_num:"+section_num
            dep = get_depth(section_num)
            if dep == 1:
                print >>opF,' '.join(tpc.strip().split())
            else:
                print >>opF,' '.join(tpc.strip().split()) + ':' + pg_num.strip()
        else:
            print >>opF,' '.join(tpc.strip().split()) + ':' + pg_num.strip()

def op_lt_col_mm(tpc,pg_num) :
    global curr_lt_topic, node_id
    initNumRe = re.compile('^(?P<sect_num>\d+\.?|\d+\.\d+|\d+\.\d+\.\d+)\s')
    # match() matches from the start while search() searches for pattern in entire string
    # Since using match() we could remove the ^ in the pattern as well.
    initNum = initNumRe.match(tpc.strip())
    if curr_lt_topic != '' :
        if not initNum :
            print "......Not initNum for tpc:"+tpc.strip()
            dep = get_depth(curr_lt_topic)
            op_end_tags(dep)
            if debug:
                nodeTxt = curr_lt_topic + ' ' + ' '.join(tpc.strip().split()) + ':' + pg_num.strip() + ':' + str(dep)
            else:
                nodeTxt = curr_lt_topic + ' ' + ' '.join(tpc.strip().split()) + ':' + pg_num.strip()
            print >>opF,'<node CREATED="1347382439772" ID="ID_'+str(node_id)+'" MODIFIED="1347382510988" TEXT="'+nodeTxt.encode('utf-8')+'">'
            node_id = node_id + 1
        else :
            print "......Else initNum for tpc:"+tpc.strip()
            dep = get_depth(curr_lt_topic)
            op_end_tags(dep)
            if debug:
                nodeTxt = curr_lt_topic + ':' + str(dep)
            else:
                nodeTxt = curr_lt_topic
            print >>opF,'<node CREATED="1347382439772" ID="ID_'+str(node_id)+'" MODIFIED="1347382510988" TEXT="'+nodeTxt.encode('utf-8')+'">'
            node_id = node_id + 1
            section_num = initNum.group('sect_num')
            print >>opF,"--- section_num:"+section_num
            dep = get_depth(section_num)
            op_end_tags(dep)
            if debug:
                nodeTxt = ' '.join(tpc.strip().split()) + ':' + pg_num.strip() + ':' + str(dep)
            else :
                nodeTxt = ' '.join(tpc.strip().split()) + ':' + pg_num.strip()
            print >>opF,'<node CREATED="1347382439772" ID="ID_'+str(node_id)+'" MODIFIED="1347382510988" TEXT="'+nodeTxt.encode('utf-8')+'">'
            node_id = node_id + 1
       	curr_lt_topic = ''
    else :
        initNumRe = re.compile('(PART|\d+\.?|\d+\.\d+|\d+\.\d+\.\d+)\s')
        initNum = initNumRe.match(tpc.strip())
        if initNum is not None :
            dep = get_depth(tpc.strip())
            op_end_tags(dep)
            if debug:
                nodeTxt = ' '.join(tpc.strip().split()) + ':' + pg_num.strip() + ':' + str(dep)
            else:
                nodeTxt = ' '.join(tpc.strip().split()) + ':' + pg_num.strip()
            print >>opF,'<node CREATED="1347382439772" ID="ID_3_'+str(node_id)+'" MODIFIED="1347382510988" TEXT="'+nodeTxt.encode('utf-8')+'">'
            node_id = node_id + 1
        else:
            # Take care of case when it is PART<spc><Num> which is taken as page num
            if tpc.strip().startswith('PART') or tpc.strip().startswith('CHAPTER'):
                curr_lt_topic = tpc.strip() + ' ' +pg_num.strip()

def append_rt_col_lines(tpc,pg_num) :
    global rt_col_lines, curr_rt_topic
    #print >>sys.stderr,"+++ In append_rt_col_lines:"+tpc.strip()+':'+pg_num.strip()
    initNumRe = re.compile('(\d+\.?|\d+\.\d+|\d+\.\d+\.\d+)\s')
    initNum = initNumRe.match(tpc.strip())
    if curr_rt_topic != '':
        if not initNum :
            rt_col_lines.append(curr_rt_topic + ' ' + tpc.strip() + ':' + pg_num.strip())
        else :
            rt_col_lines.append(curr_rt_topic)
            rt_col_lines.append(tpc.strip() + ':' + pg_num.strip())
        curr_rt_topic = ''
    else :
        if tpc.strip().startswith('PART') or tpc.strip().startswith('CHAPTER'):
            curr_rt_topic = tpc.strip() + ' ' + pg_num.strip()
        else :
            rt_col_lines.append(tpc.strip() + ':' + pg_num.strip())

def add_curr_lt_topic(tpc) :
    global curr_lt_topic
    if curr_lt_topic != '':
        curr_lt_topic += ' ' + ' '.join(tpc.strip().split())
    else :
        curr_lt_topic = ' '.join(tpc.strip().split())

def add_curr_rt_topic(tpc) :
    global curr_rt_topic
    if curr_rt_topic != '':
        curr_rt_topic += ' ' + tpc.strip()
    else :
        curr_rt_topic = tpc.strip()

def op_rt_col_lines_txt() :
    global rt_col_lines
    for itm in rt_col_lines:
		print >>opF,itm
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
            print >>opF,'<node CREATED="1347382439772" ID="ID_'+str(node_id)+'" MODIFIED="1347382510988" TEXT="'+nodeTxt.encode('utf-8')+'">'
            node_id = node_id + 1
    rt_col_lines = []

# Function to determine if the i/p line is to be discarded
def chk_for_discard(line):
  global curr_lt_topic
  retval = False
  # Added this check for NCERT books which have watermark
  n_line = ' '.join(line.split())
  # TODO: We need more robust logic to deduct watermarks spread across lines
  # CAUTION: Currenly num 10 below is magic !! 
  if curr_lt_topic == '' and (re.match('\s*\d+\.?\s',n_line) is None) and len(n_line) < 5:
    retval = True
  else:
    discard = re.compile('^\s*$|\s*(Contents|CONTENTS|PROOF|Proof)\s*')
    line_to_discard = discard.search(line)
    if line_to_discard is not None:
	  retval = True
  return retval

# END: Functions

# START: Main
print >>sys.stderr,"...Num. of i/p args: "+str(len(sys.argv))
if (len(sys.argv) < 4):
  print >>sys.stderr,"Usage: "+__file__+" <pdftotext i/p txt file> <mm or txt> <root node text> <opt:1|2 for col. nums>"
  sys.exit(-1)
ipF = open(sys.argv[1],'r')
# CAUTION: This code assumes a specific test directory structure
opFName = sys.argv[1].replace('real_ips','real_ops',1)
opFName = opFName.replace('.txt','.mm',1)
print >>sys.stderr,"...Writing MMap XML to file: %s" % (opFName)
opF = open(opFName,'w')
opTyp = sys.argv[2]
root_txt = sys.argv[3]
if len(sys.argv) > 4 :
    num_ip_cols = sys.argv[4]
else :
    num_ip_cols = '2' #Default is 2 columns
if opTyp == 'mm' :
    # Print the header of the .mm XML file
    print >>opF,'<map version="1.0.0">'

    # Print the first or root node
    print >>opF,'<node CREATED="1347382439772" ID="ID_'+str(node_id)+'" LINK="'+sys.argv[1]+'" MODIFIED="1347382510988" TEXT="'+root_txt+'">'
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
    if debug:
        print >>sys.stderr,"...len of cols:"+str(len(cols))+" line:"+line
        for col in cols:
            print >>sys.stderr,"......",col
    if len(cols) == 1 :
	    # Could be either left and/or right column without page number
        if len(rt_col_lines) > 0:
            if l_spcs_mo and (l_spcs_mo.end() >= 60) :
                add_curr_rt_topic(cols[0])
            else :
                add_curr_lt_topic(cols[0])
        else :
            add_curr_lt_topic(line)
        # TODO: Handle both left & right cols. texts
    elif len(cols) == 2 or len(cols) == 3 :
        # This can never happen: just print the line
        print >>sys.stderr,"...Split array has two/three segments"
    elif len(cols) == 4 :
        if cols[3].strip() != '' :
		    # Chk if this is just an i/p file of 1-col only
            if len(rt_col_lines) > 0:
                if opTyp == 'mm' :
	                op_lt_col_mm(cols[0],cols[1])
                else :
			        op_lt_col_txt(cols[0], cols[1])
                add_curr_rt_topic(cols[3])
            else :
                add_curr_lt_topic(line)
        else :
            #print >>sys.stderr, "...i/p line: "+line
            if l_spcs_mo and (l_spcs_mo.end() >= 60) :
                append_rt_col_lines(cols[0],cols[1])
            else :
                # The magic number 25 is for beginning of left col text after spaces 
                #idx_num = line.find(cols[1])
                idx_num = line.find(cols[0])
                if idx_num != -1 and idx_num < 25 :
                    if opTyp == 'mm' :
	                    op_lt_col_mm(cols[0],cols[1])
                    else :
			            op_lt_col_txt(cols[0],cols[1])
                else :
                    # Split cols[0] with more than 3 spaces & store left col & append right col
					# Giving error for NCERT books ToCs. 'coz of page watermarks. 
                    # print >>sys.stderr,"......i/p line is:"+line
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
        # This does not always mean 2 cols with pagenums present.
        # TODO: Handle the case in which there could be numbers in heading text
        if len(rt_col_lines) > 0: 
            if opTyp == 'mm' :
	            op_lt_col_mm(cols[0],cols[1])
            else :
                op_lt_col_txt(cols[0],cols[1])
            append_rt_col_lines(cols[3],cols[4])
        else :
            tpc_l = ' '.join([ cols[0], cols[1], cols[3] ])
            pg_num_l = cols[4]
            op_lt_col_txt(tpc_l,pg_num_l)
    elif len(cols) == 8 or len(cols) == 9 :
        # This can never happen: just print the line
        print >>sys.stderr,"...Split array has eight/nine segments"
    elif len(cols) == 10 :
		# This is definitely a line with one number in the section heading text
	    # The number could be either in left or right col
        tpc_l = pg_num_l = tpc_r = pg_num_r = ''
        idx_c1 = line.find(cols[1])
        if idx_c1 <= 50 :
            # Num is in left col text
            tpc_l = ' '.join([ cols[0], cols[1], cols[3] ])
            pg_num_l = cols[4]
            tpc_r = cols[6]
            pg_num_r = cols[7]
        else :
	        # Num is in the right col text
            tpc_l = cols[0]
            pg_num_l = cols[1]
            tpc_r = ' '.join([ cols[3], cols[4], cols[6] ])
            pg_num_r = cols[7]
        if opTyp == 'mm' :
	        op_lt_col_mm(tpc_l,pg_num_l)
        else :
            op_lt_col_txt(tpc_l,pg_num_l)
        append_rt_col_lines(tpc_r,pg_num_r)
    else :
        print >>sys.stderr,"...Length of split string with num more than 10:"
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
    print >>opF,'</node>'
    print >>opF,'</map>'
# Check if the XML o/p is well-formed
try:
	parseXmlFile(opFName)
	print >>sys.stderr,"XML file: %s is well-formed" % (opFName)
except Exception, e:
	print >>sys.stderr,"Error is %s" % (e)

ipF.close()
opF.close()
