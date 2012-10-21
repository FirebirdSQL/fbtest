#!/usr/bin/python
#
#   PROGRAM/MODULE: 
#   FILE:           fbtest.py
#   DESCRIPTION:    Firebird QA system
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

import sys
import types
import os
import platform
import tempfile
import re
import difflib
import operator
import itertools
import pickle
import weakref
import traceback
from StringIO import StringIO
import fdb as kdb
import fdb.services as fbservice
from fdb.ibase import DB_CHAR_SET_NAME_TO_PYTHON_ENCODING_MAP

try:
    from subprocess import Popen, PIPE
except ImportError:
    from subprocess25 import Popen, PIPE

DB_NEW            = 'New'
DB_EXISTING       = 'Existing'
DB_RESTORE        = 'Restore'
DB_ACCESS         = [None, DB_NEW, DB_EXISTING, DB_RESTORE]
CHARACTER_SETS    = [None, 'NONE','ASCII','BIG_5','CYRL','DOS437','DOS737','DOS775',
                    'DOS850','DOS852','DOS857','DOS858','DOS860','DOS861','DOS862',
                    'DOS863','DOS864','DOS865','DOS866','DOS869','EUCJ_0208','GBK',
                    'GB_2312','ISO8859_1','ISO8859_2','ISO8859_3','ISO8859_4',
                    'ISO8859_5','ISO8859_6','ISO8859_7','ISO8859_8','ISO8859_9',
                    'ISO8859_13','KOI8R','KOI8U','KSC_5601','NEXT','OCTETS',
                    'SJIS_0208','TIS620','UNICODE_FSS','UTF8','WIN1250','WIN1251',
                    'WIN1252','WIN1253','WIN1254','WIN1255','WIN1256','WIN1257',
                    'WIN1258','LATIN2']
PAGE_SIZES        = [None,'1024','2048','4096','8192','16384']
TYPE_ISQL         = 'ISQL'
TYPE_PYTHON       = 'Python'
TEST_TYPES        = [TYPE_ISQL,TYPE_PYTHON]
PLATFORMS         = ['Windows','Linux','MacOS','FreeBSD','Solaris','HP-UX']
UNKNOWN           = 'Unknown'

def trim_value(value):
    """Return string with trailing whitespaces from each line removed."""
    return '\n'.join((row.rstrip() for row in value.split('\n')))
def quote(value):
    """Return properly quoted string according it's content."""
    single = value.find("'")
    double = value.find('"')
    multiline = value.find('\n') != -1
    if multiline or ((single != -1) and (double != -1)):
        if value.find('"""') == -1 and value[0] != '"' and value[-1] != '"':
            s = '"""%s"""' % value
        else:
            s = "'''%s'''" % value
    elif (single != -1) and (double == -1):
        s = '"%s"' % value
    else:
        s = "'%s'" % value
    return s
def compare_versions(lver, rver):
    """ Compare two version strings, returns:
    0 for lver = rver
    -1 for lver < rver
    1 for lver > rver"""
    if lver == None:
        lver = "0"
    if rver == None:
        rver = "0"
    lverlist = lver.split(".")[:3]
    rverlist = rver.split(".")[:3]
    if len(rverlist) < len(lverlist):
        for i in range(len(lverlist)-len(rverlist)):
            rverlist.append("0")
    if len(rverlist) > len(lverlist):
        for i in range(len(rverlist)-len(lverlist)):
            lverlist.append("0")
    for i in range(len(rverlist)):
        if (int(rverlist[i]) > int(lverlist[i])):
            return -1
        if (int(rverlist[i]) < int(lverlist[i])):
            return 1
    return 0
def as_unicode(value):
    """Make sure that string is unicode.
    Accepts Unicode, strings encoded in UTF-8 or None and returns Unicode
    string or None.
    """
    assert value is None or isinstance(value,types.StringTypes)
    if isinstance(value,types.StringType):
        return value.decode('utf-8')
    else:
        return value
def as_utf8(value):
    """Make sure that string is encoded in UTF-8.
    Accepts Unicode, strings or None. If paremeter is unicode, it's returned as
    string encoded in UTF-8. String or None parameter is returned as is.
    """
    assert value is None or isinstance(value,types.StringTypes)
    if isinstance(value,types.UnicodeType):
        return value.encode('utf-8')
    else:
        return value
    
def runProgram(args,environment,stdin=None,**kwargs):
    """Run external program using Popen from subprocess module and capture stdin and stderr.
    
    :args: List of arguments for :class:s`subprocess.Popen`. First must be
           specification of program to run.
    :environment: Dictionary of environment variables. Ignored in this version.
    :stdin: String to be passed as stdin to external program.
    :kwarg: Dictionary of additional keyword arguments for Popen.
    
    Returns tuple of (returncode,stdout,stderr)
    """
    if stdin:
        kwargs['stdin'] = PIPE
    p = Popen(args,stdout=PIPE,stderr=PIPE,**kwargs)
    (stdout,stderr) = p.communicate(stdin)
    return (p.returncode,stdout,stderr)

class TestVersion(object):
    """Recipe for test execution against specific Firebird version and OS platform.
    """
    FIELDS = ['id','qmid','firebird_version','platform','database','database_name',
              'backup_file','user_name','user_password','database_character_set',
              'connection_character_set','page_size','sql_dialect','init_script',
              'test_type','test_script','expected_stdout','expected_stderr',
              'resources','substitutions']
    
    def __init__(self, id, platform, firebird_version, test_type,
                  test_script, database=DB_NEW, expected_stdout='', expected_stderr = '',
                  database_name = None, backup_file = None, user_name = 'SYSDBA', 
                  user_password = 'masterkey', database_character_set = None,
                  connection_character_set = None, page_size = None, 
                  sql_dialect = 3, init_script = '', resources= None,
                  substitutions = None,qmid=None):

        assert database_character_set in CHARACTER_SETS
        assert connection_character_set in CHARACTER_SETS
        #assert platform in PLATFORMS
        assert page_size in PAGE_SIZES
        assert database in DB_ACCESS

        self.id = id
        self.qmid = qmid
        self.platform = platform
        self.firebird_version = firebird_version
        self.database = database
        self.database_name = database_name
        self.backup_file = backup_file
        self.user_name = user_name
        self.user_password = user_password
        self.database_character_set = database_character_set
        self.connection_character_set = connection_character_set
        self.page_size = page_size
        self.sql_dialect = sql_dialect
        self.init_script = as_unicode(init_script)
        self.test_type = test_type
        self.test_script = as_unicode(test_script)

        self.expected_stdout = as_unicode(expected_stdout)
        self.expected_stderr = as_unicode(expected_stderr)
        self.resources = resources
        self.substitutions = []
        if substitutions:
            for (pattern,replacement) in substitutions:
                self.substitutions.append((as_unicode(pattern),
                                           as_unicode(replacement)))

    def get_platforms(self):
        if self.platform == 'All':
            return PLATFORMS
        else:
            return self.platform.split(':')
    def run(self,context,result):
        """Execute the recipe.
        
        :context: :class:`Runner` instance.
        :result:  :class:`result` instance.
        """

        def fb15bandaid(self):
            if self.init_script and self.init_script[-1] != '\n':
                self.init_script = self.init_script+'\n'
            if self.test_script and self.test_script[-1] != '\n':
                self.test_script = self.test_script+'\n'
        def fail_and_annotate_streams(outcome, program_name, cause, stdout=None, 
                                   stderr=None, annotate={}):
            """Set test as FAILed and set annotations. Used to note failures
            from external programs.
            """
            annotations = dict(annotate)
            unexp=[]
            if stdout:
                unexp.append("stdout")
                annotations["%s_STDOUT" % program_name]= stdout
            if stderr: # gbak prints nothing to stderr if everything went ok
                unexp.append("stderr")
                annotations["%s_STDERR" % program_name]= stderr
            if unexp: # if we got something in stdout, stderr or both 
                cause += "\nUnexpected " + " and ".join(unexp) + \
                        " stream%s " % "s"[len(unexp)==1:] + \
                        "received from %s." % program_name
            result.set_outcome(outcome,cause,annotations)
        def substitute_macros(text):
            """Substitute macros for context values."""
            f_text = text
            for (pattern,replacement) in context.environment.items():
                replacement = replacement.replace(os.path.sep,'/')
                f_text = f_text.replace('$(%s)' % pattern.upper(), replacement)
            return f_text
        def string_strip(string, isql=True, remove_space=True):
            """Remove unwanted isql noise strings and apply substitutions defined
            in recipe to captured output string.
            """
            if not string:
                return string
            if isql:
                for regex in isqlsubs:
                    string = re.sub(regex, "", string)
            for pattern, replacement in self.substitutions:
                string= re.compile(pattern, re.M).sub(replacement, string)
            if remove_space:
                string = space_strip(string)
            return string
        def space_strip(string):
            """Reduce spaces in string"""
            string= re.sub("(?m)^\s+", "", string)
            return re.sub("(?m)\s+$", "", string)
        def annotate_diff(desc, stdout_e, stdout_a, stdout_e_strp, stdout_a_strp):
            """Set test as FAILed due to difference in actual and expected stdout
            and set annotations accordingly.
            """
            id_str= "%s_" % desc
            result[id_str + "stdout_expected"]         = stdout_e
            result[id_str + "stdout_actual"]           = stdout_a
            result[id_str + "stdout_expected_stripped"]= stdout_e_strp
            result[id_str + "stdout_actual_stripped"]  = stdout_a_strp
            result[id_str + "stripped_diff"]           = '\n'.join( difflib.ndiff( stdout_e_strp.splitlines(),
                stdout_a_strp.splitlines() ))
            result.fail("Expected standard output from %s does not match actual output." % desc)
        def annotate_error_diff(desc, stderr_e, stderr_a, stderr_e_strp, stderr_a_strp):
            """Set test as FAILed due to difference in actual and expected stderr
            and set annotations accordingly.
            """
            id_str= "%s_" % desc
            result[id_str + "stderr_expected"]         = stderr_e
            result[id_str + "stderr_actual"]           = stderr_a
            result[id_str + "stderr_expected_stripped"]= stderr_e_strp
            result[id_str + "stderr_actual_stripped"]  = stderr_a_strp
            result[id_str + "stderr_stripped_diff"]    = '\n'.join( difflib.ndiff( stderr_e_strp.splitlines(),
                stderr_a_strp.splitlines() ))
            result.fail("Expected error output from %s does not match actual error output." % desc)
        def python_data_printer(cur):
            """Print data from open KInterbasDB cursor to stdout."""
            # Print a header.
            for fieldDesc in cur.description:
                print fieldDesc[kdb.DESCRIPTION_NAME].ljust(fieldDesc[kdb.DESCRIPTION_DISPLAY_SIZE]) ,
            print
            for fieldDesc in cur.description:
                print "-" * max((len(fieldDesc[kdb.DESCRIPTION_NAME]),fieldDesc[kdb.DESCRIPTION_DISPLAY_SIZE])),
            print
            # For each row, print the value of each field left-justified within
            # the maximum possible width of that field.
            fieldIndices = range(len(cur.description))
            for row in cur:
                for fieldIndex in fieldIndices:
                    fieldValue = str(row[fieldIndex])
                    fieldMaxWidth = max((len(cur.description[fieldIndex][kdb.DESCRIPTION_NAME]),cur.description[fieldIndex][kdb.DESCRIPTION_DISPLAY_SIZE]))
                    print fieldValue.ljust(fieldMaxWidth) ,
                print
        def run_program_from_python_test(program, args, stdin=''):
            """Helper method to run external programs from tests written in Python.
            stdout and stderr from program are written to stdout and stderr.
            """
            #environ = self.__MakeEnvironment()
            # PC: fix values so they are strings. Needed for Windows.
            #for key in environ.iterkeys():
                #environ[key] = str(environ[key])
            # provide full path for standard tools
            program = context.environment.get('%s_path' % program, program)
            basename = os.path.split(program)[-1]
            args.insert(0,program)

            if self.connection_character_set:
                args.extend(['-ch',self.connection_character_set])
                script = stdin.encode(DB_CHAR_SET_NAME_TO_PYTHON_ENCODING_MAP[self.connection_character_set])
            else:
                script = stdin.encode('ascii')
            script = substitute_macros(script)
            try:
                return_code, stdout, stderr = runProgram(args,[],stdin=script)
                sys.stdout.writelines(stdout)
                sys.stderr.writelines(stderr)
            except:
                result.note_exception(cause="Python test: Exception raised while running external program from Python test.")
                result["failing_program"] = program
                cleanup()

        def cleanup():
            """Cleanup after the test run."""
            if connection:
                try:
                    if not connection.closed:
                        connection.close()
                except:
                    result.note_exception(cause="Exception raised while closing database.")
                    result["db_unable_to_close"] = dsn
            if cleanup_db:
                params = {'dsn':cleanup_db,'user':self.user_name.encode('ascii'),'password':self.user_password.encode('ascii')}
                try:
                    c = kdb.connect(**params)
                    c.drop_database()
                except:
                    result.note_exception(cause="Test cleanup: Exception raised while dropping database.")
                    return

        if context.version.startswith('1.5'):
            fb15bandaid()
        
        isqlsubs= map(re.compile,['(?m)Database:.*\n?', 'SQL>[ \t]*\n?', 
                                  'CON>[ \t]*\n?', '-->[ \t]*\n?'])
        cause = 'Unknown cause'
        cleanup_db = None
        connection = None
        if self.database_name:
            db_name = self.database_name
        else:
            db_name = self.id + '.fdb'
        dsn = os.path.join(context.tempdir, db_name)
        if context.server_location:
            dsn = context.server_location + dsn
        context.environment['DSN'] = dsn

        try:
            # Prepare database if needed
            if self.database == DB_NEW:
                createCommand = "CREATE DATABASE '%s' USER '%s' PASSWORD '%s'" % (dsn,
                    self.user_name,
                    self.user_password)
                if self.page_size:
                    createCommand += " PAGE_SIZE=%d" % int(self.page_size)
                if self.database_character_set:
                    createCommand += " DEFAULT CHARACTER SET %s" % self.database_character_set
                try:
                    conn= kdb.create_database(createCommand, self.sql_dialect)
                    conn.close()
                except KeyboardInterrupt:
                    cleanup_db = dsn
                    raise
                except:
                    result.note_exception(cause="Test setup: Exception raised while creating database.")
                    result["db_unable_to_create"] = dsn
                    return
                else:
                    cleanup_db = dsn
            elif self.database == DB_RESTORE:
                try:
                    return_code, stdout, stderr= runProgram([context.gbak_path, "-C", 
                        "-user",     self.user_name,
                        "-password", self.user_password,
                        os.path.join(context.repository.backup_location,self.backup_file), 
                        dsn],[])
                except KeyboardInterrupt:
                    cleanup_db = dsn
                    raise
                except:
                    result.note_exception(cause="Test setup: Database restore failed.")
                    result["db_unable_to_restore"] = dsn
                    return
                else:
                    if stdout or stderr:
                        fail_and_annotate_streams(Result.ERROR,'GBAK','Database restore',
                                               stdout,stderr)
                        return
                    else:
                        cleanup_db = dsn
            elif self.database == DB_EXISTING:
                dsn = os.path.join(context.repository.suite_database_location, db_name)
                if context.server_location:
                    dsn = context.server_location + dsn
                params = {'dsn':dsn,'user':self.user_name,'password':self.user_password,
                          'dialect':self.sql_dialect}
                if self.connection_character_set:
                    params['charset'] = self.connection_character_set
                try:
                    connection = kdb.connect(**params)
                except KeyboardInterrupt:
                    raise
                except:
                    result.note_exception(cause="Test setup: Exception raised while connecting to database.")
                    return
    
            # Execute Init script
            if self.init_script:
                params = [context.isql_path,dsn,'-user',self.user_name,'-password',
                          self.user_password]
                if self.connection_character_set:
                    params.extend(['-ch',self.connection_character_set])
                    script = self.init_script.encode(DB_CHAR_SET_NAME_TO_PYTHON_ENCODING_MAP[self.connection_character_set])
                else:
                    script = self.init_script.encode('ascii')
                script = substitute_macros(script)
                try:
                    return_code, stdout, stderr= runProgram(params,[],stdin=script)
                except KeyboardInterrupt:
                    raise
                except:
                    result.note_exception(cause="Test setup: Exception raised while running init script.")
                    result["failing_script"] = self.init_script.encode('utf-8')
                    cleanup()
                    return
                else:
                    if stderr:
                        if self.connection_character_set:
                            stderr = stderr.decode(DB_CHAR_SET_NAME_TO_PYTHON_ENCODING_MAP[self.connection_character_set]).encode('utf-8')
                        fail_and_annotate_streams(Result.ERROR,'ISQL','Init script',stderr=stderr)
                        cleanup()
                        return
    
            # Run test
            if self.test_type == TYPE_ISQL:
                params = [context.isql_path,dsn,'-user',self.user_name,'-password',
                          self.user_password]
                if self.connection_character_set:
                    params.extend(['-ch',self.connection_character_set])
                    script = self.test_script.encode(DB_CHAR_SET_NAME_TO_PYTHON_ENCODING_MAP[self.connection_character_set])
                else:
                    script = self.test_script.encode('ascii')
                script = substitute_macros(script)
                try:
                    return_code, stdout, stderr= runProgram(params,[],stdin=script)
                except KeyboardInterrupt:
                    raise
                except:
                    result.note_exception(cause="Exception raised while running ISQL test script.")
                    result["failing_script"] = self.test_script
                else:
                    # First, convert it to unicode
                    if stdout:
                        if self.connection_character_set:
                            stdout = stdout.decode(DB_CHAR_SET_NAME_TO_PYTHON_ENCODING_MAP[self.connection_character_set])
                        else:
                            stdout = stdout.decode('ascii')
                    if stderr:
                        if self.connection_character_set:
                            stderr = stderr.decode(DB_CHAR_SET_NAME_TO_PYTHON_ENCODING_MAP[self.connection_character_set])
                        else:
                            stderr = stderr.decode('ascii')
                    # Create stripped versions
                    stdout_stripped = string_strip(stdout) # strip whole stdout
                    stdout_e_stripped = string_strip(self.expected_stdout) # strip whole expected stdout
                    stderr_stripped = string_strip(stderr) # strip whole stderr
                    stderr_e_stripped = string_strip(self.expected_stderr) # strip whole expected stderr
                    # Analyze results
                    if stderr_stripped != stderr_e_stripped: # if error outputs do not match
                        annotate_error_diff("ISQL",
                            self.expected_stderr,
                            stderr,
                            stderr_e_stripped,
                            stderr_stripped)
                    elif stdout_stripped == stdout_e_stripped: # if they match
                        pass
                    else:
                        annotate_diff("ISQL",
                            self.expected_stdout,
                            stdout,
                            stdout_e_stripped,
                            stdout_stripped)
            else:
                # test is written in Python
                if not connection and self.database != None:
                    params = {'dsn':dsn,'user':self.user_name.encode('ascii'),'password':self.user_password.encode('ascii'),
                              'dialect':self.sql_dialect}
                    if self.connection_character_set:
                        params['charset'] = self.connection_character_set
                    try:
                        connection = kdb.connect(**params)
                    except KeyboardInterrupt:
                        raise
                    except:
                        result.note_exception(cause="Test setup: Exception raised while connecting to database.")
                        cleanup()
                        return
    
                global_ns={
                    'context'           : context.environment,
                    'kdb'               : kdb,
                    'printData'         : python_data_printer,
                    'runProgram'        : run_program_from_python_test,
                    'sys'               : sys,
                    'dsn'               : dsn,
                    'user_name'         : self.user_name.encode('ascii'),
                    'user_password'     : self.user_password.encode('ascii'),
                    'page_size'         : self.page_size,
                    'sql_dialect'       : self.sql_dialect,
                    'character_set'     : self.connection_character_set,
                    #'server_location'   : context["server_location"],
                    #'database_location' : context[self.db_path_property],
                    'db_conn'           : connection,
                    'db_path_property'  : 'database_location',
                    }
                local_ns={}
    
                saved_out = sys.stdout
                saved_err = sys.stderr
                try:
                    sys.stdout = StringIO()
                    sys.stderr = StringIO()
                    exec substitute_macros(self.test_script) in global_ns, local_ns
                except KeyboardInterrupt:
                    raise
                except:
                    result.note_exception(cause="Exception raised while executing Python test script.")
                else:
                    stdout_a = ''
                    try:
                        stdout_a = sys.stdout.getvalue()
                        if self.connection_character_set:
                            stdout_a = stdout_a.decode(DB_CHAR_SET_NAME_TO_PYTHON_ENCODING_MAP[self.connection_character_set])
                        else:
                            stdout_a = stdout_a.decode('ascii')
                    except  UnicodeDecodeError:
                        result.note_exception(cause="Exception raised while processing stdout from Python test script.")
                    try:
                        stderr_a = sys.stderr.getvalue()
                        if self.connection_character_set:
                            stderr_a = stderr_a.decode(DB_CHAR_SET_NAME_TO_PYTHON_ENCODING_MAP[self.connection_character_set])
                        else:
                            stderr_a = stderr_a.decode('ascii')
                    except  UnicodeDecodeError:
                        result.note_exception(cause="Exception raised while processing stderr from Python test script.")
    
                    stdout_e_stripped= string_strip(self.expected_stdout)
                    stdout_a_stripped= string_strip(stdout_a)
                    stderr_e_stripped= string_strip(self.expected_stderr)
                    stderr_a_stripped= string_strip(stderr_a)
                    if stderr_a_stripped != stderr_e_stripped: # if error outputs do not match
                        annotate_error_diff("Python", 
                                          self.expected_stderr, stderr_a,
                                          stderr_e_stripped, stderr_a_stripped)
                    elif stdout_a_stripped == stdout_e_stripped:
                        pass
                    else:
                        annotate_diff("Python", 
                                     self.expected_stdout, stdout_a, 
                                     stdout_e_stripped, stdout_a_stripped)
                finally:
                    sys.stdout = saved_out
                    sys.stderr = saved_err
                    for conn in (obj for (name,obj) in itertools.chain(global_ns.items(),local_ns.items())
                                 if isinstance(obj,kdb.Connection) and name != 'db_conn'):
                        if not conn.closed:
                            conn.close()
            # Cleanup
            cleanup()
        except KeyboardInterrupt:
            cleanup()
            raise
            

    def as_expression(self):
        """Return recipe data as string definition of Python dictionary.
        This string could be evaluated back to Python dictionary and passed to
        TestVersion constructor to recreate the test version instance.
        String is encoded in UTF-8 if necessary.
        """
        def store(attr,value):
            if value and attr in ['firebird_version','platform','init_script',
                                  'test_script','expected_stdout','expected_stderr',
                                  'resources','substitutions','test_type']:
                return True
            elif attr == 'database' and value in [None,DB_EXISTING,DB_RESTORE]:
                return True
            elif attr == 'database_name' and value and self.database in [None,DB_EXISTING]:
                return True
            elif attr == 'backup_file' and self.database == DB_RESTORE:
                return True
            elif attr == 'user_name' and value != 'SYSDBA':
                return True
            elif attr == 'user_password' and (value != 'masterkey' or self.user_name != 'SYSDBA'):
                return True
            elif attr == 'database_character_set' and value and value != 'NONE':
                return True
            elif attr == 'connection_character_set' and value and value != 'NONE':
                return True
            elif attr == 'page_size' and value:
                return True
            elif attr == 'sql_dialect' and value != 3:
                return True
            else:
                return False

        data = [(key,self.__dict__[key]) for key in self.FIELDS]
        items = []
        for (key,value) in data:
            if not store(key,value):
                continue
            if isinstance(value,types.UnicodeType):
                value = value.encode('utf-8')
            if isinstance(value,types.StringTypes):
                value = trim_value(value)
            if key in ['database_name','expected_stderr','expected_stdout',
                       'init_script','test_script']:
                items.append(" '%s': %s" % (key,quote(value)))
            elif isinstance(value,types.StringType):
                items.append(" '%s': %s" % (key,quote(value)))
            elif key == 'substitutions':
                l = []
                for (pattern,replacement) in value:
                    if isinstance(pattern,types.UnicodeType):
                        pattern = pattern.encode('utf-8')
                    if isinstance(replacement,types.UnicodeType):
                        replacement = replacement.encode('utf-8')
                    l.append('(%s,%s)' % (quote(pattern),quote(replacement)))
                items.append(" '%s': %s" % (key,'[%s]' % ','.join(l)))
            elif key == 'resources':
                l = []
                for res in value:
                    l.append(quote(res))
                items.append(" '%s': %s" % (key,'[%s]' % ','.join(l)))
            else:
                items.append(" '%s': %s" % (key,str(value)))
        r = '{\n%s\n}' % ',\n'.join(items)
        return r

class Test(object):
    """Test definition.
    
    Can contain multiple recipes for test execution against different Firebird
    versions on various OS platforms.
    """
    FIELDS = ['id','qmid','tracker_id','title','description','min_versions','versions']

    def __init__(self,id,title='',description='',tracker_id='',min_versions=None,
                 versions=None,qmid=None):
        self.id = id
        self.qmid = qmid
        self.tracker_id = tracker_id
        self.title = as_unicode(title)
        self.description = as_unicode(description)
        self.min_versions = min_versions
        self.versions = []
        if versions:
            for version in versions:
                self.add_version(TestVersion(id,**version))
    def add_version(self,version):
        """Add :classL`TestVersion` instance to test.
        """
        assert self.id == version.id
        self.versions.append(version)
    def as_expression(self):
        """Return test data as string definition of Python dictionary.
        This string could be evaluated back to Python dictionary and passed to
        Test constructor to recreate the test instance.
        String is encoded in UTF-8 if necessary.
        """
        data = [(key,self.__dict__[key]) for key in self.FIELDS]
        items = []
        for (key,value) in data:
            if isinstance(value,types.UnicodeType):
                value = value.encode('utf-8')
            if isinstance(value,types.StringTypes):
                value = trim_value(value)
            if isinstance(value,types.StringType):
                items.append("'%s': %s" % (key,quote(value)))
            elif key == 'versions':
                l = []
                for version in self.versions:
                    l.append(version.as_expression())
                items.append("'%s': [\n%s\n]" % (key,'%s' % ',\n'.join(l)))
            else:
                items.append("'%s': %s" % (key,str(value)))
        r = '{\n%s\n}' % ',\n'.join(items)
        return r
    def get_name(self):
        return self.id.split('.')[-1:][0]
    def get_version_for(self,platform,version):
        """Return test recipe suitable for specified platform and Firebird version."""
        def supports_platform(test_platforms):
            if test_platforms.upper() in ['ALL','ANY']:
                platforms = PLATFORMS
            else:
                platforms = test_platforms.split(':')
            return platform in platforms
        
        # Minimal required version check (for mainline releases)
        if self.min_versions:
            base_version = '.'.join(version.split('.')[:2])
            for base_min_version, min_version in (('.'.join(x.split('.')[:2]),x)
                                                  for x in self.min_versions.split(';')):
                if compare_versions(base_version,base_min_version) == 0:
                    if compare_versions(version,min_version) < 0:
                        return None
        # Find the suitable test version
        candidate = '0'
        test = None
        for t in (t for t in self.versions if supports_platform(t.platform)):
            if compare_versions(version,t.firebird_version) >= 0:
                if compare_versions(candidate,t.firebird_version) < 0:
                    candidate = t.firebird_version
                    test = t
        return test

class Resource(object):
    """Base class for test resources.
    """
    def __init__(self,id):
        self.id = id
    def as_expression(self):
        """Return resource data as string definition of Python dictionary.
        This string could be evaluated back to Python dictionary and passed to
        Resource constructor to recreate the resource instance.
        String is encoded in UTF-8 if necessary.
        """
        data = [(key,self.__dict__[key]) for key in self.FIELDS]
        items = []
        for (key,value) in data:
            if isinstance(value,types.UnicodeType):
                value = value.encode('utf-8')
            if isinstance(value,types.StringTypes):
                value = trim_value(value)
            if isinstance(value,types.StringType):
                items.append("'%s': %s" % (key,quote(value)))
            else:
                items.append("'%s': %s" % (key,str(value)))
        r = '{\n%s\n}' % ',\n'.join(items)
        return r
    @classmethod
    def create(cls,kind,**kwargs):
        """Class method to create right Resource instance from parameters.
        """
        if kind == 'user':
            return UserResource(**kwargs)
        else:
            raise Exception("Unknown resource type '%s'" % kind)
    def fail_and_annotate_streams(self, result, outcome, program_name, cause,
                                  stdout=None, stderr=None, annotate={}):
        """Helper method to note fail resource setup/cleanup in Result instance."""
        annotations = dict(annotate)
        unexp=[]
        if stdout:
            unexp.append("stdout")
            annotations["%s_STDOUT" % program_name]= stdout
        if stderr: # gbak prints nothing to stderr if everything went ok
            unexp.append("stderr")
            annotations["%s_STDERR" % program_name]= stderr
        if unexp: # if we got something in stdout, stderr or both 
            cause += "\nUnexpected " + " and ".join(unexp) + \
                    " stream%s " % "s"[len(unexp)==1:] + \
                    "received from %s." % program_name
        result.set_outcome(outcome,cause,annotations)
    def setup(self,context,result):
        """Resource initialization"""
        pass
    def cleanup(self,result):
        """Resource finalization"""
        pass

class UserResource(Resource):
    """Test resource that provides Firebird USER.
    """
    FIELD = ['id','user_name','user_password']

    def __init__(self,id,user_name,user_password):
        super(UserResource,self).__init__(id)
        self.user_name = user_name
        self.user_password = user_password
        self.do_cleanup = False
    def setup(self,context,result):
        try:
            return_code, stdout, stderr= runProgram([context.gsec_path,
                "-user",     context.user_name,
                "-password", context.user_password,
                "-add", self.user_name,
                "-pw", self.user_password],[])
        except:
            result.note_exception(cause="Resource setup: Can't add user.")
            result["user_name"] = self.user_name
            return
        else:
            if return_code != 0:
                self.fail_and_annotate_streams(result,Result.ERROR,'GSEC','Add new user',
                                       stdout,stderr)
                return
            else:
                self.do_cleanup = True
    def cleanup(self,context,result):
        if self.do_cleanup:
            try:
                return_code, stdout, stderr= runProgram([context.gsec_path,
                    "-user",     context.user_name,
                    "-password", context.user_password,
                    "-delete", self.user_name],[])
            except:
                result.note_exception(cause="Resource cleanup: Can't remove user.")
                result["user_name"] = self.user_name
                return
            else:
                if return_code != 0:
                    self.fail_and_annotate_streams(result, Result.ERROR,'GSEC','Delete user',
                                           stdout,stderr)
    
class Suite(object):
    """Container for tests and sub-suites to organize tests in hierarchical structure.
    
    attributes:
    :name:   Suite name.
    :parent: Parent suite or None.
    :suites: Dictionary of sub-suites
    :tests:  List of tests.
    :path:   Directory with tests and sub-suites.
    """
    def __init__(self,name,path=None,parent=None):
        self.name = name
        if parent:
            self.parent = weakref.ref(parent)
        else:
            self.parent = None
        self.suites = {}
        self.tests = []
        if path:
            self.path = path
        else:
            if parent:
                self.path = os.path.join(parent.path,self.name)
            else:
                raise Exception('Either path or parent must be specified')
        if not os.path.isdir(self.path):
            if not os.path.exists(self.path):
                os.mkdir(self.path)
            else:
                raise Exception('Path is not a directory')
            
    def clear(self):
        """Delete all tests a sub-suites"""
        for test in self.tests:
            del test
        self.tests = []
        for suite in self.suites:
            suite.clear()
            del suite
        self.suites = {}
    def get_parent(self):
        """Return parent suite or None"""
        if self.parent:
            return self.parent()
        else:
            return None
    def get_id(self):
        """Return suite ID.
        Consists from suite names from root to this one separated by dot."""
        p = self.get_parent()
        if p:
            parent_id = p.get_id()
            if parent_id:
                return '.'.join((parent_id,self.name))
            else:
                return self.name
        else:
            return self.name
    def get_tests(self):
        """Return all tests for this suite (including tests from sub-suites)."""
        subtests = itertools.chain(*(s.get_tests() for s in self.suites.values()))
        tt = [t for t in itertools.chain(self.tests,subtests)]
        return tt
    def load(self):
        """Load tests and sub-suites."""
        assert self.path != None
        self.clear()
        dirlist = os.listdir(self.path)
        for dirname in (name for name in dirlist if os.path.isdir(os.path.join(self.path,name))):
            suite = Suite(dirname,parent=self)
            suite.load()
            self.suites[suite.name] = suite
        for testname in (name for name in dirlist if os.path.isfile(os.path.join(self.path,name)) and
                         os.path.splitext(name)[1].lower() == '.fbt'):
            try:
                f = open(os.path.join(self.path,testname),'rU')
                expr = f.read()
                d = eval(expr)
                test_id = os.path.splitext(testname)[0].lower()
                suite_id = self.get_id()
                if suite_id:
                    test_id = '.'.join((suite_id,test_id))
                d['id'] = test_id
                self.tests.append(Test(**d))
            except:
                print "Error loading test '%s'" % os.path.join(self.path,testname)
                raise
            finally:
                f.close()
    def reload_test(self,test_id):
        l = test_id.split('.')
        if len(l) > 1:
            s_name = l[:1][0]
            if s_name in self.suites:
                self.suites[s_name].reload_test('.'.join(l[1:]))
            else:
                raise Exception("Unknown suite '%s'" % '.'.join([self.get_id(),s_name]))
        else:
            suite_id = self.get_id()
            if suite_id:
                test_id = '.'.join((suite_id,test_id))
            test = [t for t in self.tests if t.id == test_id]
            if len(test) >= 0:
                test = test[0]
                self.tests.remove(test)
            else:
                raise Exception("Unknown test '%s'" % test_id)
            testfile = test_id.split('.')[-1:][0]+'.fbt'
            
            if os.path.isfile(os.path.join(self.path,testfile)):
                try:
                    f = open(os.path.join(self.path,testfile),'rU')
                    expr = f.read()
                    d = eval(expr)
                    d['id'] = test_id
                    self.tests.append(Test(**d))
                finally:
                    f.close()
    def save_test(self,test_id):
        l = test_id.split('.')
        if len(l) > 1:
            self.suites[l[:1][0]].save_test('.'.join(l[1:]))
        else:
            suite_id = self.get_id()
            if suite_id:
                test_id = '.'.join((suite_id,test_id))
            test = [t for t in self.tests if t.id == test_id]
            if len(test) >= 0:
                test = test[0]
            else:
                raise Exception("Unknown test '%s'" % test_id)
            testfile = test.id.split('.')[-1:][0]+'.fbt'
            try:
                f = open(os.path.join(self.path,testfile),'w')
                f.write(test.as_expression())
                f.write('\n')
            finally:
                f.close()
    def add_test(self,test):
        l = test.id.split('.')
        s_obj = self
        while len(l) > 0:
            s_name = l.pop(0)
            if len(l) > 0:
                if s_name in s_obj.suites:
                    s_obj = s_obj.suites[s_name]
                else:
                    new_suite = Suite(s_name,parent=s_obj)
                    s_obj.suites[s_name] = new_suite
                    s_obj = new_suite
        s_obj.tests.append(test)

class Repository(object):
    """Test repository.
    
    attributes:
    :path:  Directory where repository resides.
    :test_path: Path with tests (root suite path). 'tests' subdirectory by default.
    :files_location: Path with special files. 'files' subdirectory by default.
    :backup_location: Path with db backup files. 'fbk' subdirectory by default.
    :suite_database_location: Path with databases. 'fdb' subdirectory by default.
    :result_archive: Path where test results are stored. 'archive' subdirectory by default.
    :resources: Path with test resources. 'resources' subdirectory by default.
    
    All subdirectories must exists except 'archive' that's created if necessary.
    """
    def __init__(self,repository_path):
        self.resource_map = {}
        
        # Repository data
        self.path = repository_path
        self.test_path = os.path.join(repository_path,'tests')
        self.files_location = os.path.join(repository_path,'files')
        self.backup_location = os.path.join(repository_path,'fbk')
        self.suite_database_location = os.path.join(repository_path,'fdb')
        self.result_archive = os.path.join(repository_path,'archive')
        self.resources = os.path.join(repository_path,'resources')
        if not os.path.exists(self.result_archive):
            os.makedirs(self.result_archive)
        
        self.suite = Suite('',path=self.test_path)
    def load(self):
        """Load all tests and resources.
        """
        self.suite.load()
        self.resource_map = {}
        dirlist = os.listdir(self.resources)
        for resource_name in (name for name in dirlist 
                              if os.path.isfile(os.path.join(self.resources,name)) and 
                              os.path.splitext(name)[1].lower() == '.fbr'):
            try:
                f = open(os.path.join(self.resources,resource_name),'rU')
                expr = f.read()
                d = eval(expr)
                resource_id = os.path.splitext(resource_name)[0].lower()
                d['id'] = resource_id
                kind = d['kind']
                del d['kind']
                self.resource_map[resource_id] = Resource.create(kind,**d)
            finally:
                f.close()
    def get_suite(self,suite_id=''):
        """Return suite with specified ID or None if it doesn't exists."""
        if suite_id == '':
            return self.suite
        path = suite_id.split('.')
        suite = self.suite
        for suite_name in path:
            if not suite_name in suite.suites:
                return None
            else:
                suite = suite.suites[suite_name]
        return suite
    def get_test(self,test_id):
        """Return test with specified ID or None if it doesn't exists."""
        for test in self.suite.get_tests():
            if test.id == test_id:
                return test
        return None
    def archive(self,results):
        """Store collection of results to the archive.
        Archive is structured in subdirectories. Each directory is after Firebird
        version and contains result collection dump (pickle) files with name::
            <platform><cpuarch>-<fbarch>-<person-id><sequence>.trf
        """
        path = os.path.join(self.result_archive,results.version)
        if not os.path.exists(path):
            os.makedirs(path)
        seq = 1
        while True:
            output_file = os.path.join(path,
                '%s%s-%s-%s%i.trf' % (results.platform,results.cpuarch,
                                       results.arch,results.person_id,seq))
            if os.path.isfile(output_file):
                seq += 1
            else:
                break
        results.dump(os.path.join(path,output_file))

class Result(object):
    """Result from test run or resource setup/cleanup.
    
    Also acts as dictionary of annotations.
    
    class attributes:
    :kinds:    List of possible Result kinds.
    :outcomes: List of possible outcomes:
    
    Constants:
    :FAIL:     Outcome
    :ERROR:    Outcome
    :UNTESTED: Outcome
    :PASS:     Outcome
    
    :TEST:             Kind
    :RESOURCE_SETUP:   Kind
    :RESOURCE_CLEANUP: Kind
    
    :CAUSE:      Annotation name
    :EXCEPTION:  Annotation name
    :RESOURCE:   Annotation name
    :TRACEBACK:  Annotation name
    :START_TIME: Annotation name
    :END_TIME:   Annotation name
    """

    # Constants for result kinds.

    RESOURCE_SETUP = "resource_setup"
    RESOURCE_CLEANUP = "resource_cleanup"
    TEST = "test"
    
    # Constants for outcomes.

    FAIL = "FAIL"
    ERROR = "ERROR"
    UNTESTED = "UNTESTED"
    PASS = "PASS"

    # Constants for predefined annotations.

    CAUSE = "cause"
    EXCEPTION = "exception"
    RESOURCE = "resource"
    #TARGET = "target"
    TRACEBACK = "traceback"
    START_TIME = "start_time"
    END_TIME = "end_time"
    
    # Other class variables.

    kinds = [ RESOURCE_SETUP, RESOURCE_CLEANUP, TEST ]
    outcomes = [ ERROR, FAIL, UNTESTED, PASS ]

    def __init__(self, kind, id, outcome=PASS, annotations={}):
        assert kind in Result.kinds
        assert outcome in Result.outcomes

        self.id = id
        self.kind = kind
        self.outcome = outcome
        self.annotations = annotations.copy()

    # These methods allow 'Result' to act like a dictionary of
    # annotations.
    
    def set_outcome(self, outcome, cause = None, annotations = {}):
        """Set Result outcome.
        
        :cause: Short description of the outcome
        :annotations: Disctionary of result anntotations.
        """
        assert outcome in Result.outcomes
        self.outcome = outcome
        if cause:
            self.set_cause(cause)
        self.annotate(annotations)
    def annotate(self, annotations):
        """Set annotations"""
        self.annotations.update(annotations)
    def fail(self, cause = None, annotations = {}):
        """Set FAIL outcome with specified cause and annotations"""
        self.set_outcome(Result.FAIL, cause, annotations)
    def error(self, cause = None, annotations = {}):
        """Set ERROR outcome with specified cause and annotations"""
        self.set_outcome(Result.ERROR, cause, annotations)
    def get_cause(self):
        """Return cause"""
        if self.has_key(Result.CAUSE):
            return self[Result.CAUSE]
        else:
            return ""
    def set_cause(self, cause):
        """Set cause"""
        self[Result.CAUSE] = cause
    def note_exception(self,
                      exc_info = None,
                      cause = None,
                      outcome = ERROR):
        """Set outcome to ERROR and annotate with exception info and traceback."""
        if not exc_info:
            exc_info = sys.exc_info()

        exception_type = exc_info[0]
        
        # If no cause was specified, use an appropriate message.
        if not cause:
            cause = "An exception occurred."

        self.set_outcome(outcome, cause)
        self[Result.EXCEPTION] \
            = "%s: %s" % exc_info[:2]
        self[Result.TRACEBACK] \
            = '\n'.join(traceback.format_tb(exc_info[2]))

    def __getitem__(self, key):
        assert type(key) in types.StringTypes
        return self.annotations[key]
    def __setitem__(self, key, value):
        assert type(key) in types.StringTypes
        assert type(value) in types.StringTypes
        self.annotations[key] = value
    def __delitem__(self, key):
        assert type(key) in types.StringTypes
        del self.annotations[key]
    def get(self, key, default=None):
        assert type(key) in types.StringTypes
        return self.annotations.get(key, default)
    def has_key(self, key):
        assert type(key) in types.StringTypes
        return self.annotations.has_key(key)
    def keys(self):
        return self.annotations.keys()
    def items(self):
        return self.annotations.items()

class RunResults(object):
    """Collection of test/resource Results.
    
    Designed to hold Results from single QA run. Acts also as dictionary of Results
    with test/resource ID as key and Result object as value.
    
    attributes:
    :results:     Dictionary of :class:`Result` objects. Key is test/resource ID.
    :description: QA run description
    :version:     Firebird version
    :cpuarch:     CPU architecture
    :arch:        Firebird architecture
    :platform:    OS platform
    :person_id:   QA person ID
    :person:      QA person name
    """
    def __init__(self):
        self.results = {}
        self.description = ''
        self.version = UNKNOWN
        self.cpuarch = UNKNOWN
        self.arch = UNKNOWN
        self.platform = UNKNOWN
        self.person_id = 'XX'
        self.person_name = UNKNOWN
        self.sequence = 0
    def clear(self):
        """Remove results"""
        self.results = {}
    def add(self,result):
        """Add result"""
        self.results[result.id] = result

    def __getitem__(self, key):
        assert type(key) in types.StringTypes
        return self.results[key]
    def __setitem__(self, key, value):
        assert type(key) in types.StringTypes
        assert type(value) == Result
        self.results[key] = value
    def __delitem__(self, key):
        assert type(key) in types.StringTypes
        del self.results[key]
    def get(self, key, default=None):
        assert type(key) in types.StringTypes
        return self.results.get(key, default)
    def has_key(self, key):
        assert type(key) in types.StringTypes
        return self.results.has_key(key)
    def keys(self):
        return self.results.keys()
    def items(self):
        return self.results.items()
    def values(self):
        return self.results.values()

    def get_outcomes(self):
        """Get list outcomes from stored Results"""
        return [r.outcome for r in self.values()]
    def dump(self,filename):
        """Store (pickle) collection to file."""
        try:
            f = open(filename,'w')
            pickle.dump(self,f)
        finally:
            f.close()
    @classmethod
    def load(cls,filename):
        """Load results from file"""
        obj = None
        f = open(filename,'r')
        try:
            obj = pickle.load(f)
        finally:
            f.close()
        return obj
    def get_passes(self):
        """Return list of Results with PASS outcome"""
        return [result for result in self.values() if result.outcome == Result.PASS]
    def get_untested(self):
        """Return list of Results with UNTESTED outcome"""
        return [result for result in self.values() if result.outcome == Result.UNTESTED]
    def get_errors(self):
        """Return list of Results with ERROR outcome"""
        return [result for result in self.values() if result.outcome == Result.ERROR]
    def get_fails(self):
        """Return list of Results with FAIL outcome"""
        return [result for result in self.values() if result.outcome == Result.FAIL]
    def get_pass_count(self):
        """Return number of PASS outcomes"""
        return sum(1 for outcome in (r.outcome for r in self.values()) if outcome == Result.PASS)
    def get_error_count(self):
        """Return number of ERROR outcomes"""
        return sum(1 for outcome in (r.outcome for r in self.values()) if outcome == Result.ERROR)
    def get_untested_count(self):
        """Return number of UNTESTED outcomes"""
        return sum(1 for outcome in (r.outcome for r in self.values()) if outcome == Result.UNTESTED)
    def get_fail_count(self):
        """Return number of FAIL outcomes"""
        return sum(1 for outcome in (r.outcome for r in self.values()) if outcome == Result.FAIL)
    def save(self,filename):
        """Write text report to file"""
        f = open(filename,'w')
        f.write('Test results for %s v%s\n' % (self.description,self.version))
        f.write('Series ran by %s\n\n' % self.person_name)
        for result in self.values():
            f.write('%-70s : %s\n' % (result.id,result.outcome))
            if result.outcome != Result.PASS:
                for (kind, annotation) in result.annotations.items():
                    f.write('%s:\n%s\n' % (kind, as_utf8(annotation)))
                    f.write('\n')
        f.write('\n\nPasses:   %i\n' % self.get_pass_count())
        f.write('Fails:    %i\n' % self.get_fail_count())
        f.write('Errors:   %i\n' % self.get_error_count())
        f.write('Untested: %i\n' % self.get_untested_count())
        f.close()
    def printSummary(self):
        """Print results summary to stdout"""
        #outcomes = self.get_outcomes()
        #passes   = 'Passes:   %i' % sum(1 for outcome in outcomes if outcome == Result.PASS)
        #untested = 'Untested: %i' % sum(1 for outcome in outcomes if outcome == Result.UNTESTED)
        #errors   = 'Errors:   %i' % sum(1 for outcome in outcomes if outcome == Result.ERROR)
        #fails    = 'Fails:    %i' % sum(1 for outcome in outcomes if outcome == Result.FAIL)
        print
        print 'Passes:   %i' % self.get_pass_count()
        print 'Fails:    %i' % self.get_fail_count()
        print 'Errors:   %i' % self.get_error_count()
        print 'Untested: %i' % self.get_untested_count()


class Runner(object):
    """QA Execution engine.
    
    attributes:
    :repository:       :class:`Repository` object.
    :server_location:  Firebird server host specification.
    :user_name:        Firebird user name (SYSDBA by default).
    :user_password:    Firebird user password ('masterkey' by default).
    :fbdir:            Root directory of Firebird installation.
    :version:          Firebird version
    :arch:             Firebird architecture.
    :platform:         OS platform
    :cpuarch:          CPU architecture
    :isql_path:        Path to ISQL
    :gbak_path:        Path to GBAK
    :gsec_path:        Path to GSEC
    :gstat_path:       Path to GSTAT
    :gfix_path:        Path to GFIX
    :gpre_path:        Path to GPRE
    :security_db:      Path to security database.
    :person_name:      QA person name
    :person_id:        QA person ID (two letters)
    :run_description:  Short QA run description
    :sequence:          QA run sequence number
    :environment:      Dictionary with QA environment configuration
    :tempdir:          Path to working directory
    """
    def __init__(self,repository):

        # Repository data
        self.repository = repository

        # Target environment data
        self.server_location = ''
        self.user_name = 'SYSDBA'
        self.user_password = 'masterkey'
        self.fbdir = None
        self.version = UNKNOWN
        self.arch = UNKNOWN
        if sys.platform == 'win32':
            self.platform = 'Windows'
        elif sys.platform.startswith('linux'):
            self.platform = 'Linux'
        elif sys.platform.startswith('darwin'):
            self.platform = 'MacOS'
        else:
            self.platform = UNKNOWN
        self.cpuarch = platform.architecture()[0][:2]
        # test context variables
        self.isql_path = None
        self.gbak_path = None
        self.gsec_path = None
        self.gstat_path = None
        self.gfix_path = None
        self.gpre_path = None
        self.security_db = None
        
        # Person data
        self.person_id = 'XX'
        self.person_name = UNKNOWN

        # Run environment data
        self.run_description = UNKNOWN
        self.sequence = 0
        self.environment = {'files_location': self.repository.files_location,
                            'backup_location': self.repository.backup_location,
                            'suite_database_location': self.repository.suite_database_location,
                            }
        self.tempdir = os.path.join(self.repository.path,'tmp'+os.path.sep)
        if not os.path.exists(self.tempdir):
            os.makedirs(self.tempdir)
    def _get_tempdir(self):
        return self._tempdir
    def _set_tempdir(self,value):
        self._tempdir = os.path.join(value,'') # ensure it ends with path separator
        self.environment['temp_directory'] = self._tempdir
        self.environment['database_location'] = self._tempdir
        self.environment['DATABASE_PATH'] = self._tempdir
    tempdir = property(_get_tempdir,_set_tempdir)
    def set_target(self,arch,host,bin_dir=None,password='masterkey'):
        """Configures the QA environment to run on specified Firebird installation.
        
        :arch:     Firebird architecture (SS,CS or SC).
        :host:     'LOCAL' or Firebird host machine identification.
        :password: Password for Firebird access (default 'masterkey').
        """
        self.arch = arch
        
        if host.upper() != 'LOCAL':
            self.server_location = host+':'
            svc = fbservice.connect(host=host,password=password)
        else:
            self.server_location = ''
            svc = fbservice.connect(password=password)
        
        version = svc.get_server_version()
        fbarch = svc.get_architecture().lower()
        self.version = version[4:version.index(' ')]
        fbdir = svc.get_home_directory()
        self.fbdir = fbdir
        ext = ''
        if fbarch.find('windows') != -1:
            self.platform = 'Windows'
            ext = '.exe'
        elif fbarch.find('linux') != -1:
            self.platform = 'Linux'
        elif fbarch.find('darwin') != -1:
            self.platform = 'MacOS'
        self.user_password = password
        
        # test context variables
        if bin_dir:
            self.isql_path = os.path.join(bin_dir,'isql'+ext)
            self.gbak_path = os.path.join(bin_dir,'gbak'+ext)
            self.gsec_path = os.path.join(bin_dir,'gsec'+ext)
            self.gstat_path = os.path.join(bin_dir,'gstat'+ext)
            self.gfix_path = os.path.join(bin_dir,'gfix'+ext)
            self.gpre_path = os.path.join(bin_dir,'gpre'+ext)
        else:
            self.isql_path = os.path.join(fbdir,'bin','isql'+ext)
            self.gbak_path = os.path.join(fbdir,'bin','gbak'+ext)
            self.gsec_path = os.path.join(fbdir,'bin','gsec'+ext)
            self.gstat_path = os.path.join(fbdir,'bin','gstat'+ext)
            self.gfix_path = os.path.join(fbdir,'bin','gfix'+ext)
            self.gpre_path = os.path.join(fbdir,'bin','gpre'+ext)
        self.security_db = svc.getSecurityDatabasePath()

        self.run_description = '%s%s %s' % (self.platform,self.cpuarch,self.arch)
        cntx = dict()
        cntx['server_location'] = self.server_location
        cntx['user_name'] = self.user_name.encode('ascii')
        cntx['user_password'] = self.user_password.encode('ascii')
        cntx['isql_path'] = self.isql_path
        cntx['gbak_path'] = self.gbak_path
        cntx['gsec_path'] = self.gsec_path
        cntx['gstat_path'] = self.gstat_path
        cntx['gfix_path'] = self.gfix_path
        cntx['gpre_path'] = self.gpre_path
        cntx['isc4_path'] = self.security_db
        #cntx['run_description'] = self.run_description
        self.environment.update(cntx)
    def run(self, test_list=None):
        """Run tests.
        
        paremeters:
        :test_list:  List of :class:`Test` objects to run. If not specified, runs
                     all tests in repository.
        
        Return :class:`RunResults` object with results.
        
        QA environment must be properly configured!
        """
        results = RunResults()
        results.version = self.version
        results.arch = self.arch
        results.description = self.run_description
        results.platform = self.platform
        results.person_id = self.person_id
        results.person_name = self.person_name
        results.cpuarch = self.cpuarch
        results.sequence = self.sequence

        resources = {}
        
        if not test_list:
            test_list = self.repository.suite.get_tests()
        else:
            if isinstance(test_list,Suite):
                test_list = test_list.get_tests()

        try:
            for test in test_list:
                test_recipe = test.get_version_for(self.platform,self.version)
                result = Result(Result.TEST,test.id)
                skip = False
                
                if test_recipe:
                    # handle resources
                    if test_recipe.resources:
                        for resource_name in test_recipe.resources:
                            if resource_name not in resources:
                                resource = self.repository.resource_map[resource_name]
                                res_result = Result(Result.RESOURCE_SETUP,resource.id)
                                print '%-70s :' % resource.id,
                                try:
                                    resource.setup(self,res_result)
                                except Exception:
                                    res_result.note_exception()
                                    result.set_outcome(Result.UNTESTED,'Resource setup failed')
                                    skip = True
                                else:
                                    if res_result.outcome != Result.PASS:
                                        result.set_outcome(Result.UNTESTED,'Resource setup failed')
                                        skip = True
                                print res_result.outcome
                                resources[resource.id] = (resource,res_result)
                            else:
                                # check whether the resource was set up
                                (resource,res_result) = resources[resource_name]
                                if res_result.outcome != Result.PASS:
                                    result.set_outcome(Result.UNTESTED,'Resource setup failed')
                                    skip = True
                    
                    print '%-70s :' % test.id,
                    if not skip:
                        try:
                            test_recipe.run(self,result)
                        except Exception:
                            result.note_exception()
                    print result.outcome
                    if result.outcome != Result.PASS:
                        print result.get_cause()
                    results.add(result)
                #else:
                    #result.set_outcome(Result.UNTESTED,'No recipe for %s on %s' % (self.version,self.platform))
        except KeyboardInterrupt:
            print
            print 'Keyboard Interrupt'

        # resource cleanup
        for (resource,res_result) in resources.values():
            if res_result.outcome == Result.PASS:
                res_result = Result(Result.RESOURCE_CLEANUP,resource.id)
                print '%-70s :' % resource.id,
                try:
                    resource.cleanup(self,res_result)
                except Exception:
                    res_result.note_exception()
                print res_result.outcome
        
        results.printSummary()
        return results

try:
    import rpyc
    rpyc_available = True

    class FBTestService(rpyc.Service):
        def on_connect(self):
            self._conn._config['allow_public_attrs'] = True
            self._conn._config['allow_setattr'] = True
            self._conn._config['allow_pickle'] = True
        def exposed_get_Test(self):
            return Test
        def exposed_get_TestVersion(self):
            return TestVersion
        def exposed_get_Result(self):
            return Result
        def exposed_get_Resource(self):
            return Resource
        def exposed_get_repository(self):
            return repository
        def exposed_get_runner(self):
            return runner

except ImportError:
    rpyc_available = False
    
if __name__=='__main__':
    from optparse import OptionParser
    
    parser = OptionParser("usage: %prog [options] [suite_or_test_name]")
    parser.add_option('-b','--bin-dir',help='Directory where Firebird binaries tools are')
    parser.add_option('-d','--db-dir',help='Directory to use for test databases')
    parser.add_option('-r','--rerun',action='store_true',help="Run only tests that don't PASSed in last run")
    parser.add_option('-u','--update',action='store_true',help="Update last run results with re-run results")
    parser.add_option('-w','--password',default='masterkey',help='SYSDBA password')
    parser.add_option('-o','--host', default='localhost',help='Firebird host machine identification')
    if rpyc_available:
        parser.add_option('-s','--server',action='store_true',help="Run fbtest as RPyC slave server")
        parser.add_option('-g','--register',action='store_true',help="Run fbtest as RPyC slave server")
    parser.add_option('-a','--arch',help='Firebird architecture: SS, CS, SC')
    parser.add_option('-q','--sequence',type='int',help='Run sequence number for this target')
    #parser.add_option('-p','--person',help='QA person name')
    #parser.add_option('--archive',action='store_true',help='Archive results')
    parser.set_defaults(rerun=False,update=False,server=False,register=False,sequence=1,arch='SS')

    (options,args) = parser.parse_args()
    repository = Repository(os.getcwd())
    repository.load()
    runner = Runner(repository)
    if options.db_dir:
        runner.tempdir = options.db_dir
    runner.set_target(options.arch,options.host,options.bin_dir,options.password)
    runner.sequence = options.sequence
    #if options.person:
        #runner.person_name = options.person
        #runner.person_id = options.person[:2]
    
    if rpyc_available and options.server:
        from rpyc.utils.server import ThreadedServer
        service = ThreadedServer(FBTestService, port = 18861, auto_register = options.register)
        service.start()
    else:
        if options.rerun:
            last_results = RunResults.load(os.path.join(os.getcwd(),'results.trf'))
            run_ids = [r.id for r in last_results.results.values() if r.kind == Result.TEST and 
                       r.outcome != Result.PASS]
            run_list = list(itertools.imap(repository.get_test, run_ids))
        else:
            if len(args) == 1:
                run_name = args[0]
                suite = repository.get_suite(run_name)
                if suite:
                    run_list = suite.get_tests()
                else:
                    test = repository.get_test(run_name)
                    if test:
                        run_list = [test]
                    else:
                        run_list = None
            else:
                run_list = repository.suite.get_tests()
    
        if run_list:
            results = runner.run(run_list)
            if not options.rerun:
                results.dump(os.path.join(os.getcwd(),'results.trf'))
                results.save(os.path.join(os.getcwd(),'results.txt'))
            elif options.update:
                last_results.results.update(results.results)
                last_results.dump(os.path.join(os.getcwd(),'results.trf'))
                last_results.save(os.path.join(os.getcwd(),'results.txt'))
        else:
            print 'Nothing to run'
