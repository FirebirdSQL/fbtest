#!/usr/bin/python
#
#   PROGRAM/MODULE: 
#   FILE:           fbtestconv.py
#   DESCRIPTION:    Conversion of tests from QMTest to new Firebird QA system
#   CREATED:        22.6.2009
#
#  The contents of this file are subject to the Initial
#  Developer's Public License Version 1.0 (the 'License');
#  you may not use this file except in compliance with the
#  License. You may obtain a copy of the License at
#  http://www.firebirdsql.org/index.php?op=doc&id=idpl
#
#  Software distributed under the License is distributed AS IS,
#  WITHOUT WARRANTY OF ANY KIND, either express or implied.
#  See the License for the specific language governing rights
#  and limitations under the License.
#
#  The Original Code was created by Pavel Cisar
#
#  Copyright (c) 2009 Pavel Cisar <pcisar@users.sourceforge.net>
#  and all contributors signed below.
#
#  All Rights Reserved.
#  Contributor(s): ______________________________________.

from fbtest import *

try:
    import qm
except ImportError:
    qm_present = False
else:
    qm_present = True
    import qm
    import qm.xmlutil
    from qm.test import base
    from qm.test.database import TestDescriptor
    #from qm.test.result import Result
    from qm.test.classes.xml_database import XMLDatabase
    from qm.extension import get_class_arguments
    from qm.test.cmdline import QMTest
    qm.common.program_name = "QMTest"
    qm.diagnostic.load_messages("test")
    qm.rc.Load("test")

DB_ACCESS_TRANSLATION = {"Create New":DB_NEW, "Connect To Existing":DB_EXISTING, 
                         "Restore From Backup":DB_RESTORE, "None":None}
TEST_TYPE_TRANSLATION = {"Python: String":TYPE_PYTHON, "SQL: String":TYPE_ISQL}

def version_from_qm(qmtest):
        
    a = qmtest.GetArguments()
    assert a['populate_method'] in ["Using SQL Commands", 'None (manual)']
    assert a['statement_type_and_result'] in ["Python: String", "SQL: String"]
    
    p = {}
    id = a['test_id'].encode().lower()
    qmid = qmtest.GetId().encode().lower()
    #l = qmid.split('.')[:-1]
    #l.extend(id.split('.')[-1:])
    #id = '.'.join(l)
    id = id.replace('-','_')
    p['id'] =  id
    p['qmid'] = qmid
    p['platform'] = a['target_platform'].encode()
    p['firebird_version'] = a['target_version'].encode()
    p['database'] = DB_ACCESS_TRANSLATION[a['create_db_method']]
    p['database_name'] = a['db_name']
    p['backup_file'] = a['backup_file_path'].encode()
    p['user_name'] = a['user_name'].encode()
    p['user_password'] = a['user_password'].encode()
    p['database_character_set'] = a['character_set'].encode()
    p['connection_character_set'] = a['character_set'].encode()
    if a['page_size'] != 'Default':
        p['page_size'] = a['page_size'].encode()
    else:
        p['page_size'] = None
    p['sql_dialect'] = int(a['sql_dialect'])
    p['init_script'] = as_unicode(a['isql_script'])
    if not p['init_script'].strip():
        p['init_script'] = None
    p['test_type'] = TEST_TYPE_TRANSLATION[a['statement_type_and_result']]
    p['test_script'] = as_unicode(a['source_code'])
    p['expected_stdout'] = as_unicode(a['result_string'])
    if not p['expected_stdout'].strip():
        p['expected_stdout'] = None
    p['expected_stderr'] = as_unicode(a['expected_stderr'])
    if not p['expected_stderr'].strip():
        p['expected_stderr'] = None
    subs = []
    
    if a['substitutions']:
        for (pattern,replacement) in a['substitutions']:
            subs.append((as_unicode(pattern),as_unicode(replacement)))
    p['substitutions'] = subs
    p['resources'] = a['resources']
    p['resources'] = []
    for r in a['resources']:
        p['resources'].append(r.encode())
    return TestVersion(**p)

def test_from_qm(qmtest):
    a = qmtest.GetArguments()

    p = {}
    id = a['test_id'].encode().lower()
    qmid = qmtest.GetId().lower()
    #l = qmid.split('.')[:-1]
    #l.extend(id.split('.')[-1:])
    #id = '.'.join(l)
    id = id.replace('-','_')
    p['id'] =  id
    p['qmid'] = qmid
    p['tracker_id'] = a['bug_id'].encode()
    p['title'] = as_unicode(a['title'])
    p['description'] = as_unicode(a['description'])
    test = Test(**p)
    test.add_version(version_from_qm(qmtest))
    return test

def load_from_qmtest(qmdb):
    root_suite = Suite('')

    if not qm_present:
        print "QMTest not installed.\nYou can download QMTest from www.qmtest.com.\n"
    if qm.test.database.is_database(qmdb):
        db = qm.test.database.load_database(qmdb)
        testids, suiteids = db.GetSuite('').GetAllTestAndSuiteIds()
        # testmap is a dictionary that maps our QA test IDs to list of qmtest test IDs 
        # (i.e. test variants)
        test_map = {}
        for t in testids:
            qmtest = db.GetItem('test',t)
            test = test_from_qm(qmtest)
            if test.id in test_map:
                test = test_map[test.id]
                test.add_version(version_from_qm(qmtest))
            else:
                test_map[test.id] = test
        root_suite.tests.extend(test_map.values())
    else:
        print "Path is not a valid QMTest test database"
    return root_suite

def save_suite(suite,dest_dir):
    for test in suite.tests:
        f = open(os.path.join(dest_dir,test.id+'.fbt'),'w')
        f.write(test.as_expression())
        f.write('\n')
        f.close()

if __name__=='__main__':
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option('-q','--qm-dir',help='Directory QMTest test databases')
    parser.add_option('-f','--fb-dir',help='Directory where to store converted test')
    (options,args) = parser.parse_args()

    save_suite(load_from_qmtest(options.qm_dir),options.fb_dir)
