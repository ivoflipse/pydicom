from __future__ import with_statement

# file "make_private_dict.py"
# Copyright (c) 2009 Daniel Nanz
# This file is released under the pydicom (http://code.google.com/p/pydicom/) 
# license.
# See the file license.txt included with the pydicom distribution, also
#    available at http://pydicom.googlecode.com

'''
-- Usage ------------------ (>= python 2.5, <3)---

python make_private_dict_alt.py

or

python make_private_dict_alt.py target_file_path
--------------------------------------------------

This script reads the DICOM private tag information as
maintained by the GDCM project (http://sourceforge.net/projects/gdcm/) 
from their website and prints it either to sys.stdout 
(if target_file_path == None) or to the file identified by a input
target_file_path.

The output is structured such, that for target_file_path = "_private_dict.py"
the output file can replace the current _private_dict.py file of the pydicom
source, which should allow straightforward testing.
'''

import urllib2
import cStringIO
import xml.etree.cElementTree as ET
import sys
import datetime
import os
import pprint


GDCM_URL = ''.join(('http://gdcm.svn.sf.net/viewvc/gdcm/trunk',
                    '/Source/DataDictionary/privatedicts.xml'))
UNKNOWN_NAME = 'Unknown'
PRIVATE_DICT_NAME = 'private_dictionaries'


def get_private_dict_from_GDCM(url=GDCM_URL, retired_field=''):
    '''open GDCM_URL, read content into StringIO file-like object and parse
       into an ElementTree instance
    '''   
    etree = ET.parse(cStringIO.StringIO(urllib2.urlopen(GDCM_URL).read()))
    p_dict = etree.getroot()
    entries = [entry for entry in p_dict.findall('entry')]

    private_dict = dict()
    for e in entries:
        d = dict()
        for item in  e.items():
            d[item[0]] = item[1]
        tag_string = ''.join((d['group'], d['element']))
        if d['name'] == '?':
            d['name'] = UNKNOWN_NAME
        dict_entry = (d['vr'], d['vm'], d['name'], retired_field)
        owner = d['owner']
        if owner in private_dict.keys():   
            pass
        else:
            private_dict[owner] = dict()
        curr_dict = private_dict[owner]
        curr_dict[tag_string] = dict_entry
    return private_dict


def get_introductory_text(filename, datestring):
    
    s = '\n'.join(('# ' + filename,
                   '# This file is autogenerated by "make_private_dict.py",',
                   '# from private elements list maintained by the GDCM project',
                   '# ('+ GDCM_URL + ').',
                   '# Downloaded on ' + datestring + '.',
                   '# See the pydicom license.txt file for license information on pydicom, and GDCM.',
                   '',
                   '# This is a dictionary of DICOM dictionaries.',
                   '# The outer dictionary key is the Private Creator name ("owner"),', 
                   '# the inner dictionary is a map of DICOM tag to ',
                   '# (VR, type, name, isRetired)',
                   '',
                   PRIVATE_DICT_NAME + ' = \\\n'))
    return s
    


def main():
    '''Get private dict from GDCM project. Write to sys.stdout or to output 
    file given as pathname and as the first argument to the script.
    '''
    private_dict = get_private_dict_from_GDCM()
    try:
        file_path = sys.argv[1]
    except IndexError:
        file_path = None
    
    if file_path != None:
        with open(file_path, 'wb') as fd:
            filename = os.path.basename(file_path)
            datestring = datetime.date.isoformat(datetime.date.today())
            int_text = get_introductory_text(filename, datestring)
            fd.write(int_text)
            pprint.pprint(private_dict, fd)
    else:
        pprint.pprint(private_dict)


if __name__ == '__main__':
    main()