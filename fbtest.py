#!/usr/bin/python
## -*- coding: utf-8 -*-
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
#  http://www.firebirdsql.org/en/initial-developer-s-public-license-version-1-0
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

from __future__ import print_function
import sys
import types
import os
from stat import S_IRWXU, S_IRWXG, S_IRWXO
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
from mako.template import Template
from mako.lookup import TemplateLookup
from argparse import ArgumentParser
from time import time
from xml.sax import saxutils

__version__ = "1.0"

try:
    from subprocess import Popen, PIPE
except ImportError:
    from subprocess25 import Popen, PIPE

try:
    import pysvn
    pysvn_present = True
except ImportError:
    pysvn_present = False

PYTHON_MAJOR_VER = sys.version_info[0]

#: Test Repository Subversion path
svn_repository = 'https://svn.code.sf.net/p/firebird/code/qa/fbt-repository/trunk/'
#: Constant
DB_NEW            = 'New'
#:
DB_EXISTING       = 'Existing'
#:
DB_RESTORE        = 'Restore'
#:
DB_ACCESS         = [None, DB_NEW, DB_EXISTING, DB_RESTORE]
#:
CHARACTER_SETS    = [None, 'NONE','ASCII','BIG_5','CYRL','DOS437','DOS737','DOS775',
                    'DOS850','DOS852','DOS857','DOS858','DOS860','DOS861','DOS862',
                    'DOS863','DOS864','DOS865','DOS866','DOS869','EUCJ_0208','GBK',
                    'GB_2312','ISO8859_1','ISO8859_2','ISO8859_3','ISO8859_4',
                    'ISO8859_5','ISO8859_6','ISO8859_7','ISO8859_8','ISO8859_9',
                    'ISO8859_13','KOI8R','KOI8U','KSC_5601','NEXT','OCTETS',
                    'SJIS_0208','TIS620','UNICODE_FSS','UTF8','WIN1250','WIN1251',
                    'WIN1252','WIN1253','WIN1254','WIN1255','WIN1256','WIN1257',
                    'WIN1258','LATIN2']
#:
PAGE_SIZES        = [None,'1024','2048','4096','8192','16384']
#:
TYPE_ISQL         = 'ISQL'
#:
TYPE_PYTHON       = 'Python'
#:
TEST_TYPES        = [TYPE_ISQL,TYPE_PYTHON]
#:
PLATFORMS         = ['Windows','Linux','MacOS','FreeBSD','Solaris','HP-UX']
#:
UNKNOWN           = 'Unknown'

# Invalid XML characters, control characters 0-31 sans \t, \n and \r
CONTROL_CHARACTERS = re.compile(r"[\000-\010\013\014\016-\037]")

template_base = """<%def name="title()">Firebird QA Analysis</%def>
<%! import datetime %>

<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN" "http://www.w3.org/TR/REC-html40/loose.dtd">
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<style type="text/css" media="screen" title="Normal Text">
html, body, div, span, applet, object, iframe, h1, h2, h3, h4, h5, h6, p,
blockquote, pre, a, abbr, acronym, address, big, cite, code, del, dfn, em,
font, img, ins, kbd, q, s, samp, small, strike, strong, sub, sup, tt, var,
dl, dt, dd, ol, ul, li, fieldset, form, label, legend, table, caption,
tbody, tfoot, thead, tr, th, td { margin: 0; padding: 0; border: 0; outline: 0;
  font-weight: inherit; font-style: inherit; font-size: 100%; font-family: inherit;
  vertical-align: baseline;}
:focus { outline: 0; }
body { line-height: 1; color: black; background: white; }
ol, ul { list-style: none; }
caption, th, td { text-align: left; font-weight: normal; }
blockquote:before, blockquote:after, q:before, q:after { content: ""; }
blockquote, q { quotes: "" ""; }

body { margin: 0; padding: 0; font-family: verdana, sans-serif; font-size: 69%;
  color: #000; background-color: #fff; }
h1 { font-size: 1.4em; font-weight: bold; margin-top: 0em; margin-bottom: 0em; }
h2 { font-size: 1.2em; margin: 1.2em 0em 1.2em 0em; font-weight: bold; }
h3 { font-size: 1.0em; margin: 1.2em 0em 1.2em 0em; font-weight: bold; }
h4 { font-size: 0.95em; margin: 1.2em 0em 1.2em 0em; font-weight: normal; }
h5 { font-size: 0.9em; margin: 1.2em 0em 1.2em 0em; font-weight: normal; }
h6 { font-size: 0.85em; margin: 1.2em 0em 1.2em 0em; font-weight: normal; }
pre { font-family: courier, courier-new; }

th { text-align: center; font-weight: bold; background-color: #e0e0e0; padding: 2px; }
table { border-collapse: separate; border-spacing: 2px; }
td { padding: 2px 0.5em 0 0.5em;}

.PASS { background-color: #a0f0a0; text-align: }
.FAIL { background-color: #ff9090; text-align: }
.ERROR { background-color: #ffffe0; text-align: }
.UNTESTED { background-color: #d0d0d0; text-align: }
.NA { background-color: white; text-align: center; }
.test_id { padding-left: 5px;}
.ann-o { background-color: white; padding: 2px; }
.ann-e { background-color: #ffffe0; padding: 2px; }
.cause { background-color: #ff9090; padding: 2px;}

#Container { margin: 0em auto; padding: 4px 20px 4px 20px ;
  text-align: left; /* Win IE5 */ }
#Header { position: relative; margin: 0; padding: 10px; clear: both; }
#Footer { font-size: 0.9em; color: #666; line-height: 1.3em; padding-top: 5px;clear: both; }
#Content { display: block; }


</style>
<title>${self.title()}</title>
</head>
<body>

<div id="Container">
  <div id="Header"><H1>QA Analysis for Firebird ${version}</H1></div>

  <div id="Content">${self.body()}
  </div>

  <div id="Footer">
    Generated by fbtest analyzer, ${datetime.datetime.now()}
  </div>
</div>

</body>
</html>
"""

template_detail = """<%inherit file="base.mako"/>
<H1>Details for test ${test_id}</H1>
%for group in test_detail:
<%
result = group[0]
i = 1
has_diffs = diffs_only and len([key for key in result.annotations.keys() if key.endswith('diff')]) > 0
if has_diffs:
  annotations = ((x,y) for x,y in result.annotations.items() if x.endswith('diff'))
else:
  annotations = ((x,y) for x,y in result.annotations.items() if x != result.CAUSE)
%>
<H2>${', '.join(group[1])}</H2>
<table width="100%" border=1>
<tr><th>Annotation</th><th>Value</th></tr>
<tr><td class="cause">Cause</td><td class="cause">${result.get_cause()}</td></tr>
%for key,value in annotations:
<tr>
%if (i % 2) == 0:
<td class="ann-o">${key}</td><td class="ann-o"><pre>${value}</pre></td>
%else:
<td class="ann-e">${key}</td><td class="ann-e"><pre>${value}</pre></td>
%endif
</tr>
<%
i += 1
%>
%endfor
</table>
%endfor
"""

template_main = """<%inherit file="base.mako"/>
<%
from operator import attrgetter
from itertools import groupby

platforms = [(k,len(list(g))) for k,g in groupby(results,attrgetter('platform'))]
cpuarchs = [(k,len(list(g))) for k,g in groupby(results,attrgetter('cpuarch'))]
archs = [(k,len(list(g))) for k,g in groupby(results,attrgetter('arch'))]
runs = [(k,len(list(g))) for k,g in groupby(results,attrgetter('sequence'))]

%>
<table>
<tr>
%for platform,span in platforms:
  <th colspan=${span}>${platform}</th>
%endfor
</tr>
<tr>
%for cpuarch,span in cpuarchs:
  <th colspan=${span}>${cpuarch}-bit</th>
%endfor
</tr>
<tr>
%for arch,span in archs:
  <th colspan=${span}>${arch}</th>
%endfor
</tr>
<tr>
%for run,span in runs:
  <th colspan=${span}>${run}</th>
%endfor
</tr>
%for test_id in test_order:
<% test_results = tests[test_id]  %>
<!--%for test_id,test_results in tests.items():-->
<tr>
%for result in test_results:
%if result:
<% r = result.outcome %>
%else:
<% r = 'NA' %>
%endif
<td class='${r}'>
%if result:
${result.outcome[:1]}
%else:
-
%endif
</td>
%endfor
%if test_id in test_details:
<td class="test_id"><a href="${test_id}.html">${test_id}</a></td></tr>
%else:
<td class="test_id">${test_id}</td></tr>
%endif
%endfor
</table>
"""


makolookup = TemplateLookup(output_encoding='utf-8', input_encoding='utf-8',
                            encoding_errors='replace')
makolookup.template_args['default_filters']=['decode.utf8']
makolookup.put_string('base.mako',template_base)
makolookup.put_string('main.mako',template_main)
makolookup.put_string('detail.mako',template_detail)

def xml_safe(value):
    """Replaces invalid XML characters with '?'."""
    return CONTROL_CHARACTERS.sub('?', value)
def escape_cdata(cdata):
    """Escape a string for an XML CDATA section."""
    return xml_safe(cdata).replace(']]>', ']]>]]&gt;<![CDATA[')
def trim_value(value):
    """Return string with trailing whitespaces from each line removed."""
    return '\n'.join((row.rstrip() for row in value.split('\n')))
def quote(value):
    """Return properly quoted string according its content."""
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
    Accepts `Unicode`, `strings` encoded in UTF-8 or `None` and returns `Unicode`
    string or `None`.
    """
    assert value is None or isinstance(value,types.StringTypes)
    if isinstance(value,types.StringType):
        return value.decode('utf-8')
    else:
        return value
def as_utf8(value):
    """Make sure that string is encoded in UTF-8.
    Accepts `Unicode`, `strings` or `None`. If paremeter is unicode, it's returned as
    string encoded in UTF-8. String or `None` parameter is returned as is.
    """
    assert value is None or isinstance(value,types.StringTypes)
    if isinstance(value,types.UnicodeType):
        return value.encode('utf-8')
    else:
        return value

def runProgram(args,environment,stdin=None,**kwargs):
    """Run external program using :class:`~subprocess.Popen` from subprocess
    module and capture `stdin` and `stderr`.

    :param list args: List of arguments for :class:`subprocess.Popen`. First item
        must be specification of program to run.
    :param dict environment: Dictionary of environment variables. Ignored in this version.
    :param string stdin: String to be passed as stdin to external program.
    :param dict kwarg: Dictionary of additional keyword arguments for Popen.

    :returns: Tuple of (returncode, stdout, stderr)
    """
    if stdin:
        kwargs['stdin'] = PIPE
    p = Popen(args,stdout=PIPE,stderr=PIPE,**kwargs)
    (stdout,stderr) = p.communicate(stdin)
    return (p.returncode,stdout,stderr)

class TestVersion(object):
    """Recipe for test execution against specific Firebird version and OS platform.
    """

    #: List of attribute names that should be included in :meth:`as_expression` returned string.
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
        """
        :param string id: Test ID (dot-separated name).
        :param string platform: List of platform names separated by colon.
        :param string firebird_version: First Firebird version this test version is designed for.
        :param string test_type: Test implemetation method: "ISQL" or "Python".
        :param string test_script: Test code.
        :param string database: Database usage specification: None, "New", "Existing" or "Restore".
        :param string expected_stdout: Expected STDOUT content.
        :param string expected_stderr: Expected STDERR content.
        :param string database_name: Database file name.
        :param string backup_file: Backup file name.
        :param string user_name: User name.
        :param string user_password: User password.
        :param string database_character_set: Character set for database.
        :param string connection_character_set: Character set for connection.
        :param string page_size: Page size for database.
        :param integer sql_dialect: SQL dialect for database.
        :param string init_script: Test initialization script.
        :param list resources: List of :class:`Resource` names.
        :param list substitutions: List of substitution specifications.
        :param string qmid: Test ID from old system (QMTest).
        """

        assert database_character_set in CHARACTER_SETS
        assert connection_character_set in CHARACTER_SETS
        #assert platform in PLATFORMS
        assert page_size in PAGE_SIZES
        assert database in DB_ACCESS

        #: Test ID.
        self.id = id
        #: Legacy test ID.
        self.qmid = qmid
        #: Platform specification (list of platform names separated by colon).
        self.platform = platform
        #: Firebird version string.
        self.firebird_version = firebird_version
        #: Database specification: :data:`DB_NEW`, :data:`DB_EXISTING` or :data:`DB_RESTORE`.
        self.database = database
        #: Database name.
        self.database_name = database_name
        #: Backup file name.
        self.backup_file = backup_file
        #: Firebird user name.
        self.user_name = user_name
        #: Firebird user password.
        self.user_password = user_password
        #: Database character set.
        self.database_character_set = database_character_set
        #: Connection character set.
        self.connection_character_set = connection_character_set
        #: Page size.
        self.page_size = page_size
        #: SQL dialect.
        self.sql_dialect = sql_dialect
        #: Test initialization script.
        self.init_script = as_unicode(init_script)
        #: Test type: :data:`TYPE_ISQL` or :data:`TYPE_PYTHON`.
        self.test_type = test_type
        #: Test stcript.
        self.test_script = as_unicode(test_script)
        #: Expected `stdout` content.
        self.expected_stdout = as_unicode(expected_stdout)
        #: Expected `stderr` content.
        self.expected_stderr = as_unicode(expected_stderr)
        #: List of resource names.
        self.resources = resources
        #: List of substitution definitions.
        self.substitutions = []
        if substitutions:
            for (pattern,replacement) in substitutions:
                self.substitutions.append((as_unicode(pattern),
                                           as_unicode(replacement)))

    def get_platforms(self):
        """Returns platforms supported by this test version as list of platform
        names.
        """
        if self.platform == 'All':
            return PLATFORMS
        else:
            return self.platform.split(':')
    def run(self,context,result):
        """Execute the recipe.

        .. important:: Test run outcome is stored in :class:`Result` instance.

        :param context: :class:`Runner` instance.
        :param result:  :class:`Result` instance.
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
                print (fieldDesc[kdb.DESCRIPTION_NAME].ljust(fieldDesc[kdb.DESCRIPTION_DISPLAY_SIZE]),end=' ')
            print('')
            for fieldDesc in cur.description:
                print ("-" * max((len(fieldDesc[kdb.DESCRIPTION_NAME]),fieldDesc[kdb.DESCRIPTION_DISPLAY_SIZE])),end=' ')
            print('')
            # For each row, print the value of each field left-justified within
            # the maximum possible width of that field.
            fieldIndices = range(len(cur.description))
            for row in cur:
                for fieldIndex in fieldIndices:
                    fieldValue = row[fieldIndex]
                    if not isinstance(fieldValue,types.StringTypes):
                        fieldValue = str(fieldValue)
                    if isinstance(fieldValue,types.UnicodeType):
                        fieldValue = fieldValue.encode('utf8')
                    fieldMaxWidth = max((len(cur.description[fieldIndex][kdb.DESCRIPTION_NAME]),cur.description[fieldIndex][kdb.DESCRIPTION_DISPLAY_SIZE]))
                    print (fieldValue.ljust(fieldMaxWidth),end=' ')
                print('')
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
                #cleanup()

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
        dsn = db_filename = os.path.join(context.tempdir, db_name)
        if context.server_location:
            dsn = context.server_location + dsn
        context.environment['DSN'] = dsn
        result[Result.START_TIME] = str(time())

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
                # We'll try to attach it first to see if it doesn't already exists
                # and drop it if it does. It's probably leftover from previous test
                # failure.
                try:
                    conn = kdb.connect(dsn=dsn,user=self.user_name,
                                       password=self.user_password)
                    conn.drop_database()
                except:
                    pass
                try:
                    conn = kdb.create_database(createCommand, self.sql_dialect)
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
                dsn = db_filename = os.path.join(context.repository.suite_database_location, db_name)
                if context.server_location:
                    dsn = context.server_location + dsn
                params = {'dsn':dsn,'user':self.user_name,'password':self.user_password,
                          'sql_dialect':self.sql_dialect}
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
                              'sql_dialect':self.sql_dialect}
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
                    'print'             : print,
                    'printData'         : python_data_printer,
                    'runProgram'        : run_program_from_python_test,
                    'sys'               : sys,
                    'dsn'               : dsn,
                    'db_filename'       : db_filename,
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
        finally:
            result[Result.END_TIME] = str(time())

    def as_expression(self):
        """Return recipe data as string definition of Python dictionary.
        This string could be evaluated back to Python dictionary and passed to
        :class:`TestVersion` constructor to recreate the test version instance.
        String is encoded in UTF-8 if necessary.

        .. note:: Only attributes that haven't DEFAULT values are included.
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

    Can contain multiple :class:`TestVersion` recipes for test execution against
    different Firebird versions on various OS platforms.
    """
    #: List of attribute names that should be included in :meth:`as_expression` returned string.
    FIELDS = ['id','qmid','tracker_id','title','description','min_versions','versions']

    def __init__(self,id,title='',description='',tracker_id='',min_versions=None,
                 versions=None,qmid=None):
        """
        :param string id: Test ID (dot-separated name).
        :param string title: Test title.
        :param string description: test description.
        :param string tracker_id: JIRA entry ID this tests relates to.
        :param string min_versions: List of minimal engine versions supported by
            test (separated by semicolon).
        :param list versions: List of disctionaries with data for creation of
            :class:`TestVersion` instances.
        :param string qmid: Test ID from old system (QMTest).
        """
        #: Test ID.
        self.id = id
        #: Legacy test ID.
        self.qmid = qmid
        #: JIRA tracker ID.
        self.tracker_id = tracker_id
        #: Test title.
        self.title = as_unicode(title)
        #: Test description.
        self.description = as_unicode(description)
        #: Minimal Firebird version number this test supports.
        self.min_versions = min_versions
        #: List of :class:`TestVersion` instances.
        self.versions = []
        if versions:
            for version in versions:
                self.add_version(TestVersion(id,**version))
    def add_version(self,version):
        """Add :class:`TestVersion` instance to test.

        :param version: :class:`TestVersion` instance.
        """
        assert self.id == version.id
        self.versions.append(version)
    def as_expression(self):
        """Return test data as string definition of Python dictionary.
        This string could be evaluated back to Python dictionary and passed to
        :class:`Test` constructor to recreate the test instance.
        String is encoded in UTF-8 if necessary.

        .. note:: Only attributes that haven't DEFAULT values are included.
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
        """Return test name.

        Test name is last part of test ID.
        """
        return self.id.split('.')[-1:][0]
    def get_version_for(self,platform,version):
        """Return test recipe suitable for specified platform and Firebird version.

        :param string platform: Platform name.
        :param string version: Firebird version.
        :returns: :class:`TestVersion` or None.
        """
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
        """
        :param string id: Resource ID.
        """
        #: Resource ID.
        self.id = id
    def as_expression(self):
        """Return resource data as string definition of Python dictionary.
        This string could be evaluated back to Python dictionary and passed to
        :class:`Resource` constructor to recreate the resource instance.
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
        """Class method to create right :class:`Resource` instance from parameters.

        :param string kind: Resource class specification.
        """
        if kind == 'user':
            return UserResource(**kwargs)
        else:
            raise Exception("Unknown resource type '%s'" % kind)
    def fail_and_annotate_streams(self, result, outcome, program_name, cause,
                                  stdout=None, stderr=None, annotate={}):
        """Helper method to note fail of resource setup/cleanup in
        :class:`Result` instance.

        :param result: :class:`Result` instance.
        :param stirng outcome: Run outcome.
        :param string program_name: Program that reports the failure.
        :param string cause: Fail reason.
        :param string stdout: `stdout` content.
        :param string stderr: `stderr` content.
        :param dict annotate: Dictionary of annotations.
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
    def setup(self,context,result):
        """Resource initialization.

        Nothing in this class."""
        pass
    def cleanup(self,result):
        """Resource finalization

        Nothing in this class."""
        pass

class UserResource(Resource):
    """Test resource that provides Firebird USER.
    """
    #: List of attribute names that should be included in :meth:`~Resource.as_expression` returned string.
    FIELD = ['id','user_name','user_password']

    def __init__(self,id,user_name,user_password):
        """
        :param string id: resource ID.
        :param string user_name: Firebird user name.
        :param string user_password: Firebird user password.
        """
        super(UserResource,self).__init__(id)
        #: Firebird user name.
        self.user_name = user_name
        #: Firebird user password.
        self.user_password = user_password
        #: True if Resource should be removed.
        self.do_cleanup = False
    def setup(self,context,result):
        """Create Firebird user with specified name and password via GSEC.
        """
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
        """Remove specified Firebird user via GSEC.
        """
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

    """
    def __init__(self,name,path=None,parent=None):
        """
        :param string name: Suite name.
        :param string path: Directory with tests and sub-suites.
        :param string parent: Parent suite name or None.
        """
        #: Suite name.
        self.name = name
        if parent:
            #: Parent suite (weak reference or None).
            self.parent = weakref.ref(parent)
        else:
            self.parent = None
        #: Dictionary of sub-suites.
        self.suites = {}
        #: dictionary of tests in this suite.
        self.tests = []
        if path:
            #: Path to directory with tests and sub-suites.
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
        """Delete all tests and sub-suites from instance."""
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
        """Load tests and sub-suites from :attr:`path`."""
        assert self.path != None
        self.clear()
        dirlist = os.listdir(self.path)
        for dirname in (name for name in dirlist if os.path.isdir(os.path.join(self.path,name))
                        and not name.startswith('.')):
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
                print ("Error loading test '%s'" % os.path.join(self.path,testname))
                raise
            finally:
                f.close()
    def reload_test(self,test_id):
        """Reload test from disk.

        :param string test_id: Test ID.
        """
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
        """Save test on disk.

        :param test_id: Test ID.
        """
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
        """Add test to suite.

        :param test: :class:`Test` instance.
        """
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

class Archive(object):
    """Run results archive.

    Archive is structured in subdirectories. Each directory is named after Firebird
    version and contains result collection dump (pickle) files with name::

    <number_of_tests_executed>-<platform><cpuarch>-<fbarch>-<person-id>-<sequence>.trf
    """
    def __init__(self,archive_path):
        """
        :param string archive_path: Directory with archive.
        """
        self.archive_path = archive_path
        if not os.path.exists(self.archive_path):
            os.makedirs(self.archive_path)
    def get_archive_filename(self,results):
        return '%04i-%s%s-%s-%s%i.trf' % (len(results.results),results.platform,
                                          results.cpuarch,results.arch,
                                          results.person_id,results.sequence)
    def get_archive_file_path(self,results):
        """Get File path for archived results.
        :param :class:`RunResult` results: Run results.
        :returns: File path.
        """
        path = os.path.join(self.archive_path,results.version)
        if not os.path.exists(path):
            os.makedirs(path)
        return os.path.join(path,self.get_archive_filename(results))
    def list_filenames(self):
        """Get list of result files in archive.
        :returns: Sorted list of filenames (including FB version subdirectory name).
        """
        l = []
        for path, dirs, files in os.walk(self.archive_path):
            for file in files:
                l.append(os.path.relpath(os.path.join(path,file),self.archive_path))
        l.sort()
        return l
    def store(self, results):
        """Store run results into archive.
        :param :class:`RunResult` results: Run results.
        """
        filename = self.get_archive_file_path(results)
        results.dump(filename)
    def retrieve(self,version=None):
        """Get list of run results from archive.

        :param string version: Returns only results for specified Firebird version.

        :returns: List of :class:`RunResult` instances.
        """
        result = []
        groups = (os.path.split(x) for x in self.list_filenames())
        groups2 = itertools.groupby(groups,operator.itemgetter(0))
        groups3 = ((k,[x[1] for x in g]) for k,g in groups2)
        for (result_version, filenames) in groups3:
            if not version or version == result_version:
                for filename in filenames:
                    filename = os.path.join(self.archive_path,result_version,filename)
                    result.append(RunResults.load(filename))
        return result
    def delete(self,result):
        """Remove specified run results from archive.

        :param result: File path in archive or :class:`RunResult` instance stored
                       in archive.
        """
        path = self.get_archive_file_path(result) if isinstance(result,RunResults) else result
        if os.path.exists(path):
            os.remove(path)

class Repository(object):
    """Test repository.

    All subdirectories must exists except 'archive' that's created if necessary.
    """
    def __init__(self,repository_path):
        """
        :param string repository_path: Directory with test repository.
        """
        #: Directory of resources that maps resource name to :class:`Resource` instances.
        self.resource_map = {}

        # Repository data
        #: Path to Repository.
        self.path = repository_path
        #: Path to tests.
        self.test_path = os.path.join(repository_path,'tests')
        #: Path to files.
        self.files_location = os.path.join(repository_path,'files')
        #: Path to database backup files.
        self.backup_location = os.path.join(repository_path,'fbk')
        #: Path to pre-created databases.
        self.suite_database_location = os.path.join(repository_path,'fdb')
        # Make sure it's accessible to Firebird
        os.chmod(self.suite_database_location,S_IRWXU | S_IRWXG | S_IRWXO)
        #: Path to archive.
        self.result_archive = Archive(os.path.join(repository_path,'archive'))
        #: Path to resources.
        self.resources = os.path.join(repository_path,'resources')

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
        """Return suite with specified ID.

        :returns: :class:`Suite` instance or `None`.
        """
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
        """Return test with specified ID.

        :returns: :class:`Test` instance or `None`.
        """
        for test in self.suite.get_tests():
            if test.id == test_id:
                return test
        return None

class Result(object):
    """Result from test run or resource setup/cleanup.

    .. note:: Also acts as dictionary of annotations.

    """

    # Constants for result kinds.

    #: Result KIND
    RESOURCE_SETUP = "resource_setup"
    #: Result KIND
    RESOURCE_CLEANUP = "resource_cleanup"
    #: Result KIND
    TEST = "test"

    # Constants for outcomes.

    #: Outcome
    FAIL = "FAIL"
    #: Outcome
    ERROR = "ERROR"
    #: Outcome
    UNTESTED = "UNTESTED"
    #: Outcome
    PASS = "PASS"

    # Constants for predefined annotations.

    #: Annotation.
    CAUSE = "cause"
    #: Annotation.
    EXCEPTION = "exception"
    #: Annotation.
    RESOURCE = "resource"
    #TARGET = "target"
    #: Annotation.
    TRACEBACK = "traceback"
    #: Annotation.
    START_TIME = "start_time"
    #: Annotation.
    END_TIME = "end_time"

    # Other class variables.

    #: List of possible result KINDS
    kinds = [ RESOURCE_SETUP, RESOURCE_CLEANUP, TEST ]
    #: List of possible OUTCOMES.
    outcomes = [ ERROR, FAIL, UNTESTED, PASS ]

    def __init__(self, kind, id, outcome=PASS, annotations={}):
        """
        :param string kind: Result kind.
        :param string id: Result ID.
        :param string outcome: Result outcome (default :data:`PASS`).
        :param dict annotations: Annotations.
        """
        assert kind in Result.kinds
        assert outcome in Result.outcomes

        #: Test ID.
        self.id = id
        #: Result Kind
        self.kind = kind
        #: Run Outcome
        self.outcome = outcome
        #: Run annotations
        self.annotations = annotations.copy()

    def set_outcome(self, outcome, cause = None, annotations = {}):
        """Set Result outcome.

        :param string outcome: Run outcome.
        :param string cause: Short description of the outcome,
        :param dict annotations: Disctionary of result anntotations.
        """
        assert outcome in Result.outcomes
        self.outcome = outcome
        if cause:
            self.set_cause(cause)
        self.annotate(annotations)
    def annotate(self, annotations):
        """Set annotations.

        :param dict annotations: Annotations.
        """
        self.annotations.update(annotations)
    def fail(self, cause = None, annotations = {}):
        """Set FAIL outcome with specified cause and annotations.

        :param string cause: Fail cause.
        :param dict annotations: Annotations.
        """
        self.set_outcome(Result.FAIL, cause, annotations)
    def error(self, cause = None, annotations = {}):
        """Set ERROR outcome with specified cause and annotations.

        :param string cause: Error cause.
        :param dict annotations: Annotations.
        """
        self.set_outcome(Result.ERROR, cause, annotations)
    def get_cause(self):
        """Return cause."""
        if self.has_key(Result.CAUSE):
            return self[Result.CAUSE]
        else:
            return ""
    def set_cause(self, cause):
        """Set cause."""
        self[Result.CAUSE] = cause
    def note_exception(self,exc_info = None, cause = None):
        """Set outcome to ERROR and annotate with exception info and traceback.

        :param exc_info: Exception info or None to use current exception info.
        :param string cause: Exception cause or `None` for default message.
        """
        if not exc_info:
            exc_info = sys.exc_info()

        exception_type = exc_info[0]

        # If no cause was specified, use an appropriate message.
        if not cause:
            cause = "An exception occurred."

        self.set_outcome(Result.ERROR, cause)
        exc = exc_info[1]
        msg = StringIO()
        print(exc.__class__.__name__ + ':',file=msg)
        for arg in exc.args:
            print(arg,file=msg)
        self[Result.EXCEPTION] \
            = msg.getvalue()
        self[Result.TRACEBACK] \
            = '\n'.join(traceback.format_tb(exc_info[2]))
    def get_run_time(self):
        start_time = float(self.get(self.START_TIME,'0.0'))
        end_time = float(self.get(self.END_TIME,'0.0'))
        return end_time - start_time

    # Next methods allow 'Result' to act like a dictionary of
    # annotations.

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
    with test/resource ID as key and :class:`Result` object as value.

    """
    def __init__(self):
        #: Dictionary of :class:`Result` objects. Key is test/resource ID.
        self.results = {}
        #: QA run description.
        self.description = ''
        #: Firebird version.
        self.version = UNKNOWN
        #: CPU architecture.
        self.cpuarch = UNKNOWN
        #: Firebird architecture.
        self.arch = UNKNOWN
        #: OS platform.
        self.platform = UNKNOWN
        #: QA person ID.
        self.person_id = 'XX'
        #: QA person name.
        self.person_name = UNKNOWN
        #: Test run sequence number.
        self.sequence = 0
        #: None or name of this instance was load from.
        self.filename = None
    def _quoteattr(self, attr):
        """Escape an XML attribute. Value can be unicode."""
        attr = xml_safe(attr)
        if isinstance(attr, unicode) and not UNICODE_STRINGS:
            attr = attr.encode(self.encoding)
        return saxutils.quoteattr(attr)
    def clear(self):
        """Remove all results."""
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
        """Store (pickle) collection of :class:`Result` instances to file."""
        try:
            f = open(filename,'w')
            pickle.dump(self,f)
        finally:
            f.close()
    @classmethod
    def load(cls,filename):
        """Load results from file.

        :param string filename: Filename with pickled :class:`Result`.
        """
        obj = None
        f = open(filename,'r')
        try:
            obj = pickle.load(f)
            obj.filename = filename
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
        """Write text report to file.

        :param string filename: Filename.
        """
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
    def save_xunit(self,filename):
        """Write xunit XML report to file.

        :param string filename: Filename.
        """
        f = open(filename,'w')
        f.write('<?xml version="1.0" encoding="UTF-8"?>')
        f.write('<testsuite name="fbtest" tests="%i" errors="%i" failures="%i" skip="%i">' %
                (len(self.results),self.get_error_count(),self.get_fail_count(),
                 self.get_untested_count()))
        for result in self.values():
            if result.outcome == Result.PASS:
                f.write('<testcase classname="Test" name="%s" time="%.3f" />' % (
                result.id,result.get_run_time()))
            else:
                f.write('<testcase classname="Test" name="%s" time="%.3f">' % (
                result.id,result.get_run_time()))
                if result.outcome == Result.ERROR:
                    if result.has_key(Result.EXCEPTION):
                        e = result[Result.EXCEPTION]
                        exc = e[:e.find(':')]
                        msg = e[e.find(':')+2:]
                        exc = exc[exc.find("'")+1:exc.rfind("'")]
                        msg = msg.lstrip()
                        f.write('<error type=%s message=%s>' % (self._quoteattr(exc),
                                                                self._quoteattr(msg)))
                        f.write('</error>')
                    else:
                        msg = result.get_cause()
                        f.write('<error type="error" message=%s>' % (self._quoteattr(msg)))
                        f.write('</error>')
                elif result.outcome == Result.FAIL:
                    for key in ['ISQL_stripped_diff','Python_stripped_diff',
                                'ISQL_stderr_stripped_diff',
                                'Python_stderr_stripped_diff']:
                        if result.has_key(key):
                            cdata = as_utf8(result[key])
                    f.write('<failure type="fail" message=%s>' % self._quoteattr(result.get_cause()))
                    f.write('<![CDATA[%s]]>' % escape_cdata(cdata))
                    f.write('</failure>')
                elif result.outcome == Result.UNTESTED:
                    f.write('<failure type="untested" message=%s>' % self._quoteattr(result.get_cause()))
                    f.write('</failure>')
                f.write('</testcase>')
        f.write('</testsuite>')
        f.close()
    def print_summary(self):
        """Print results summary to stdout."""
        #outcomes = self.get_outcomes()
        #passes   = 'Passes:   %i' % sum(1 for outcome in outcomes if outcome == Result.PASS)
        #untested = 'Untested: %i' % sum(1 for outcome in outcomes if outcome == Result.UNTESTED)
        #errors   = 'Errors:   %i' % sum(1 for outcome in outcomes if outcome == Result.ERROR)
        #fails    = 'Fails:    %i' % sum(1 for outcome in outcomes if outcome == Result.FAIL)
        print('')
        print ('Passes:   %i' % self.get_pass_count())
        print ('Fails:    %i' % self.get_fail_count())
        print ('Errors:   %i' % self.get_error_count())
        print ('Untested: %i' % self.get_untested_count())
    def print_report(self):
        for result in self.get_errors():
            print ('=' * 70)
            print ('ERROR:', result.id)
            print ('-' * 70)
            print (result.get_cause())
            print()
        for result in self.get_fails():
            print ('=' * 70)
            print ('FAIL:', result.id)
            print ('-' * 70)
            print (result.get_cause())
            print()
        for result in self.get_untested():
            print ('=' * 70)
            print ('UNTESTED:', result.id)
            print ('-' * 70)
            print (result.get_cause())
            print()

class Runner(object):
    """QA Execution engine.

    """
    def __init__(self,repository):
        """
        :param repository: :class:`Repository` instance.
        """

        #: :class:`Repository` object.
        self.repository = repository

        # Target environment data
        #: Firebird server host specification.
        self.server_location = ''
        #: Firebird user name (SYSDBA by default).
        self.user_name = 'SYSDBA'
        #: Firebird user password ('masterkey' by default).
        self.user_password = 'masterkey'
        #: Root directory of Firebird installation.
        self.fbdir = None
        #: Firebird version.
        self.version = UNKNOWN
        #: Firebird architecture.
        self.arch = UNKNOWN
        if sys.platform == 'win32':
            #: OS platform.
            self.platform = 'Windows'
        elif sys.platform.startswith('linux'):
            self.platform = 'Linux'
        elif sys.platform.startswith('darwin'):
            self.platform = 'MacOS'
        else:
            self.platform = UNKNOWN
        #: CPU architecture.
        self.cpuarch = platform.architecture()[0][:2]
        # test context variables
        #: Path to ISQL.
        self.isql_path = None
        #: Path to GBAK.
        self.gbak_path = None
        # :Path to NBACKUP
        self.nbackup_path = None
        #: Path to GSEC.
        self.gsec_path = None
        #: Path to GSTAT.
        self.gstat_path = None
        #: Path to GFIX.
        self.gfix_path = None
        #: Path to GPRE.
        self.gpre_path = None
        #: Path to security database.
        self.security_db = None

        # Person data
        #: QA person ID (two letters).
        self.person_id = 'XX'
        #: QA person name.
        self.person_name = UNKNOWN

        # Run environment data
        #: Short QA run description.
        self.run_description = UNKNOWN
        #: QA run sequence number.
        self.sequence = 0
        #: Dictionary with QA environment configuration.
        self.environment = {'files_location': self.repository.files_location,
                            'backup_location': self.repository.backup_location,
                            'suite_database_location': self.repository.suite_database_location,
                            }
        #: Path to working directory.
        self.tempdir = os.path.join(self.repository.path,'tmp'+os.path.sep)
        if not os.path.exists(self.tempdir):
            os.makedirs(self.tempdir)
            os.chmod(self.tempdir,S_IRWXU | S_IRWXG | S_IRWXO)
    def _get_tempdir(self):
        return self.__tempdir
    def _set_tempdir(self,value):
        self.__tempdir = os.path.join(value,'') # ensure it ends with path separator
        self.environment['temp_directory'] = self.__tempdir
        self.environment['database_location'] = self.__tempdir
        self.environment['DATABASE_PATH'] = self.__tempdir
    #: Directory for temporary files.
    tempdir = property(_get_tempdir,_set_tempdir)
    def set_target(self,arch,host,bin_dir=None,password='masterkey'):
        """Configures the QA environment to run on specified Firebird installation.

        :param string arch:     Firebird architecture (SS,CS, SC or EM).
        :param string host:     'LOCAL' or Firebird host machine identification.
        :param string password: Password for Firebird access (default 'masterkey').
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
            self.nbackup_path = os.path.join(bin_dir,'nbackup'+ext)
            self.gsec_path = os.path.join(bin_dir,'gsec'+ext)
            self.gstat_path = os.path.join(bin_dir,'gstat'+ext)
            self.gfix_path = os.path.join(bin_dir,'gfix'+ext)
            self.gpre_path = os.path.join(bin_dir,'gpre'+ext)
        else:
            self.isql_path = os.path.join(fbdir,'bin','isql'+ext)
            self.gbak_path = os.path.join(fbdir,'bin','gbak'+ext)
            self.nbackup_path = os.path.join(fbdir,'bin','nbackup'+ext)
            self.gsec_path = os.path.join(fbdir,'bin','gsec'+ext)
            self.gstat_path = os.path.join(fbdir,'bin','gstat'+ext)
            self.gfix_path = os.path.join(fbdir,'bin','gfix'+ext)
            self.gpre_path = os.path.join(fbdir,'bin','gpre'+ext)
        self.security_db = svc.get_security_database_path()

        self.run_description = '%s%s %s' % (self.platform,self.cpuarch,self.arch)
        cntx = dict()
        cntx['server_location'] = self.server_location
        cntx['user_name'] = self.user_name.encode('ascii')
        cntx['user_password'] = self.user_password.encode('ascii')
        cntx['isql_path'] = self.isql_path
        cntx['gbak_path'] = self.gbak_path
        cntx['nbackup_path'] = self.nbackup_path
        cntx['gsec_path'] = self.gsec_path
        cntx['gstat_path'] = self.gstat_path
        cntx['gfix_path'] = self.gfix_path
        cntx['gpre_path'] = self.gpre_path
        cntx['isc4_path'] = self.security_db
        #cntx['run_description'] = self.run_description
        self.environment.update(cntx)
    def set_person(self, person):
        """Set QA person identification.

        :param string person: QA person name.

        Sets `person_name` and `person_id` attributes:
        person_name = `person` in lowercase
        person_id = first two letters from uppercased `person`

        If `person` is "Unknown", the person_is is set to "XX".
        """
        if person.upper() == UNKNOWN.upper():
            self.person_name = UNKNOWN
            self.person_id = 'XX'
        else:
            self.person_name = person.lower()
            self.person_id = person.upper()[:2]
    def run(self,test_list=None,verbosity=1,results=None,no_summary=False):
        """Run tests.

        :param test_list:  List of :class:`Test` objects to run. If not specified,
            runs all tests in repository.
        :param int verbosity: Verbosity level (0, 1 or 2).
        :param bool no_summary: Do not print run summary.

        :returns: :class:`RunResults` object with results.

        .. warning:: QA environment must be properly configured!
        """
        if not results:
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

        start_time = time()
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
                                if verbosity == 2:
                                    print ('%s ... ' % resource.id,end='')
                                    sys.stdout.flush()
                                try:
                                    resource.setup(self,res_result)
                                except Exception:
                                    res_result.note_exception()
                                    result.set_outcome(Result.UNTESTED,'Resource setup failed')
                                    result.annotate(res_result)
                                    skip = True
                                else:
                                    if res_result.outcome != Result.PASS:
                                        result.set_outcome(Result.UNTESTED,'Resource setup failed')
                                        result.annotate(res_result)
                                        skip = True
                                if verbosity == 2:
                                    print (res_result.outcome)
                                resources[resource.id] = (resource,res_result)
                            else:
                                # check whether the resource was set up
                                (resource,res_result) = resources[resource_name]
                                if res_result.outcome != Result.PASS:
                                    result.set_outcome(Result.UNTESTED,'Resource setup failed')
                                    result.annotate(res_result)
                                    skip = True

                    if verbosity == 2:
                        print ('%s ... ' % test.id,end='')
                        sys.stdout.flush()
                    if not skip:
                        try:
                            test_recipe.run(self,result)
                        except Exception:
                            result.note_exception()
                    if verbosity == 2:
                        if result.outcome == Result.PASS:
                            print ('ok')
                        else:
                            print (result.outcome)
                    elif verbosity == 1:
                        if result.outcome == Result.PASS:
                            print ('.',end='')
                        else:
                            print (result.outcome[0],end='')
                        sys.stdout.flush()
                    results.add(result)
            if verbosity == 1:
                print ()
        except KeyboardInterrupt:
            print('')
            print ('Keyboard Interrupt')

        stop_time = time()
        # resource cleanup
        for (resource,res_result) in resources.values():
            if res_result.outcome == Result.PASS:
                res_result = Result(Result.RESOURCE_CLEANUP,resource.id)
                if verbosity == 2:
                    print ('%-70s :' % resource.id,end='')
                    sys.stdout.flush()
                try:
                    resource.cleanup(self,res_result)
                except Exception:
                    res_result.note_exception()
                if verbosity == 2:
                    print (res_result.outcome)

        if not no_summary:
            results.print_report()
            print ('-' * 70)
            print ('Ran %i tests in %.3fs' % (len(results.results),stop_time-start_time))

            fails = results.get_fail_count()
            errors = results.get_error_count()
            untested = results.get_untested_count()
            print ()
            if fails + errors + untested == 0:
                print ('OK')
            else:
                print ('FAILED ',end='')
                if fails > 0:
                    print ('(fails=%i)' % fails,end='')
                if errors > 0:
                    print ('(errors=%i)' % errors,end='')
                if untested > 0:
                    print ('(untested=%i)' % untested,end='')
                print()
        return results

try:
    import rpyc
    rpyc_available = True
except ImportError:
    rpyc_available = False

class ScriptRunner(object):
    """Helper class to organize script running code. Instantiated as singleton
    instance `script_runner`.
    """
    platform_table = {'windows':'Win','linux':'Linux','macos':'Mac',
                      'solaris':'Solaris','freebsd':'BSD','hp-ux':'HPUX'}

    def __init__(self):
        self.revision = None
        self.remote_fbtest = None
    def get_repository(self,options):
        """Connect to local or remote Test Repository.

        :param options: Command-line options.
        :returns: :class:`Repository` instance.
        """
        if options.remote:
            try:
                self.remote_fbtest = rpyc.connect_by_service('fbtest',
                                                        service=rpyc.SlaveService)
            except:
                if options.host:
                    remote_host = options.host
                else:
                    remote_host = 'localhost'
                self.remote_fbtest = rpyc.connect(remote_host,18861,service=rpyc.SlaveService)

            r = self.remote_fbtest.root
            repository = r.get_repository()
        else:
            repository = Repository(os.getcwd())
            repository.load()
        return repository
    def run_tests(self,options):
        """Called by :func:`~fbtest.run_tests` for command execution.
        """
        repository = self.get_repository(options)
        if options.remote:
            r = self.remote_fbtest.root
            r.set_stdout(sys.stdout)
            runner = r.get_runner()
        else:
            runner = Runner(repository)
            if options.db_dir:
                runner.tempdir = options.db_dir
            runner.set_target(options.arch,options.host,options.bin_dir,options.password)

        runner.sequence = options.sequence
        runner.set_person(options.person)

        verbosity = options.verbosity
        if options.verbose:
            verbosity = 2
        if options.quiet:
            verbosity = 0

        skip_tests = []
        if options.skip:
            skip_names = []
            if os.path.isfile(options.skip):
                skip_file = open(options.skip,'rU')
                skip_names.extend(line.rstrip() for line in skip_file.readlines())
                skip_file.close()
            else:
                skip_names.append(options.skip)
            for name in skip_names:
                suite = repository.get_suite(name)
                if suite:
                    skip_tests.extend(suite.get_tests())
                else:
                    test = repository.get_test(name)
                    if test:
                        skip_tests.append(test)
        if options.rerun:
            last_results = RunResults.load(os.path.join(os.getcwd(),'results.trf'))
            run_ids = [r.id for r in last_results.results.values() if r.kind == Result.TEST and
                       r.outcome != Result.PASS]
            run_list = list(itertools.imap(repository.get_test, run_ids))
        else:
            if options.name:
                suite = repository.get_suite(options.name)
                if suite:
                    run_list = suite.get_tests()
                else:
                    test = repository.get_test(options.name)
                    if test:
                        run_list = [test]
                    else:
                        run_list = None
            else:
                run_list = repository.suite.get_tests()

        if run_list:
            run_list = [test for test in run_list if test not in skip_tests]

        if run_list:
            if options.remote:
                results = runner.run(run_list,verbosity,RunResults())
            else:
                results = runner.run(run_list,verbosity)
            if not options.rerun:
                results.dump(os.path.join(os.getcwd(),'results.trf'))
            elif options.update:
                last_results.results.update(results.results)
                last_results.dump(os.path.join(os.getcwd(),'results.trf'))
            if options.archive:
                repository.result_archive.store(results)
            if options.xunit:
                results.save_xunit(os.path.join(os.getcwd(),'results.xml'))
        else:
            print ('Nothing to run')

    def run_server(self,options):
        """Called by :func:`~fbtest.run_server` for command execution.
        """
        repository = Repository(os.getcwd())
        repository.load()
        runner = Runner(repository)
        if options.db_dir:
            runner.tempdir = options.db_dir
        runner.set_target(options.arch,options.host,options.bin_dir,options.password)
        runner.sequence = 1
        runner.set_person(options.person)

        class FBTestService(rpyc.SlaveService):
            def on_connect(self):
                super(FBTestService,self).on_connect()
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
                return runner.repository
            def exposed_get_runner(self):
                return runner
            def exposed_set_stdout(self,stdout):
                sys.stdout = stdout
            #def exposed_getmodule(self, name):
                #"""imports an arbitrary module"""
                #return __import__(name, None, None, "*")

        from rpyc.utils.server import ThreadedServer
        service = ThreadedServer(FBTestService, port = 18861, auto_register = options.register)
        print("Starting fbtest in server mode...")
        print("Type ^C to stop it.")
        service.start()
    def get_run_tag(self,platform,cpuarch,arch,sequence):
        """Return string that could be used as key to group tests by platform, cpu,
           FB architecture and run sequence.
        """
        return '%s%s-%s-%i' % (self.platform_table[platform.lower()],cpuarch,arch.upper(),sequence)
    def print_result_info(self,result,filename):
        """Print information from result file.

        :param result: Run results.
        :type result: :class:`RunResults`
        :param string filename: Results filename.
        """
        print ('File:     %s' % filename)
        print ('Desc:     %s' % result.description)
        print ('Version:  %s' % result.version)
        print ('Arch:     %s' % result.arch)
        print ('Platform: %s' % result.platform)
        print ('CPU:      %s' % result.cpuarch)
        if hasattr(result,'sequence'):
            print ('Sequence: %s' % result.sequence)
        print ('Person:   %s (%s)' % (result.person_name,result.person_id))
        result.print_summary()
        print('')
    def print_fails(self,result,cause=False,detail=False):
        """Print IDs of tests that ended with FAIL.

        :param result: Run results.
        :type result: :class:`RunResults`
        :param bool cause: Print fail cause.
        :param bool detail: Print fail details.
        """
        fails = result.get_fails()
        if fails:
            print ('=== FAILS '+('='*60))
        for fail in fails:
            print (fail.id)
            if cause:
                print ('  ',fail.get_cause())
            if detail:
                for key in ['ISQL_stripped_diff','Python_stripped_diff',
                            'ISQL_stderr_stripped_diff',
                            'Python_stderr_stripped_diff']:
                    if fail.has_key(key):
                        print ('-' * 70)
                        print ('%s:' % key)
                        print (as_utf8(fail[key]))
                        print ()
    def print_errors(self,result,cause=False,detail=False):
        """Print IDs of tests that ended with ERROR.

        :param result: Run results.
        :type result: :class:`RunResults`
        :param bool cause: Print error cause.
        :param bool detail: Print error details.
        """
        errors = result.get_errors()
        if errors:
            print ('=== ERRORS '+('='*59))
        for error in errors:
            print (error.id)
            if cause:
                print ('  ',error.get_cause())
            if detail:
                for key in (k for k in error.keys() if k not in [Result.START_TIME,
                                                                 Result.END_TIME,
                                                                 Result.CAUSE]):
                    print ('-' * 70)
                    print ('%s:' % key)
                    print (as_utf8(error[key]))
    def print_untested(self,result,cause=False):
        """Print IDs of tests that ended with UNTESTED.

        :param result: Run results.
        :type result: :class:`RunResults`
        :param bool cause: Print cause.
        """
        untested = result.get_untested()
        if untested:
            print ('=== UNTESTED '+('='*59))
        for u in untested:
            print (u.id)
            if cause:
                print ('  ',u.get_cause())

    def print_analysis(self,version,results,tests,test_details,test_order,
                       output_dir,diffs_only):
        """Create HTML files with test run analysis.

        :param string version: Firebird version.
        :param result: Run results.
        :type result: :class:`RunResults`
        :param dict tests: Dictionary of all tests found in results; Test ID: list of results.
        :param dict test_details: Dictionary with test run results: Run tag: Result.
        :param list test_order: List that define test order in output.
        :param string output_dir: Directory for HTML output files.
        """
        def format_result(r):
            return '%s %s' % (r.outcome,r.get_cause())

        main_template = makolookup.get_template("main.mako")
        detail_template = makolookup.get_template("detail.mako")

        f = open(os.path.join(output_dir,'index.html'),'w')
        try:
            f.write(main_template.render(version=version,results=results,tests=tests,
                                   test_details=test_details,test_order=test_order))
        finally:
            f.close()

        for test_id,test_detail in test_details.items():
            #print ('Detail: %s' % test_id)
            f = open(os.path.join(output_dir,test_id+'.html'),'w')
            try:
                f.write(detail_template.render(version=version,test_id=test_id,
                                       test_detail=test_detail,diffs_only=diffs_only))
            except:
                f.write("Error while processing output.")
            finally:
                f.close()
    def annotation_filter(self,annotations):
        """Filters out annotations we don't want to compare.
        """
        result = []
        for key,value in annotations.items():
            if key not in [Result.START_TIME,Result.END_TIME]:
                result.append((key,value))
        result.sort(key=operator.itemgetter(0))
        return result
    def compare_results(self,r1,r2):
        """Compare two results for single test. Compares :attr:`~Result.kind`,
        :attr:`~Result.outcome` and :attr:`~Result.annotations`.

        :param r1: Run result.
        :type r1: :class:`Result`
        :param r2: Run result.
        :type r2: :class:`Result`

        :returns: True if both results are equal.
        """
        result = (r1.kind == r2.kind) and (r1.outcome == r2.outcome)
        if result:
            result = reduce(lambda x,y: x and y,map(lambda x,y: x == y,
                                                    self.annotation_filter(r1.annotations),
                                                    self.annotation_filter(r2.annotations)))
        return result

    def get_result_filenames(self,directory):
        """Return list of Result file filenames stored in directory.

        :param string directory: directory with result files.

        :returns: List with filenames.
        """
        return [os.path.join(directory,name) for name in os.listdir(directory)
                if os.path.isfile(os.path.join(directory,name)) and
                os.path.splitext(name)[1].lower() == '.trf']

    def analyze(self,filenames,output_dir,diffs_only=False):
        """Analyze test run results and produce HTML output.

        :param list filenames: List of result file filenames.
        :param string output_dir: Directory for HTML output files.
        """
        def okey(value):
            r = max((['PASS', 'ERROR', 'FAIL', 'UNTESTED'].index(r.outcome) for r in tests[value] if r))
            if r == 0:
                return value
            else:
                return r
        def overall_outcome_weight(results):
            return max((['PASS', 'ERROR', 'FAIL', 'UNTESTED'].index(r.outcome) for r in results if r))

        # pass 0: Load results
        results = [RunResults.load(filename) for filename in filenames]
        # step 1: Check if all results are for the same version
        version = results[0].version
        for result in results:
            if result.version != version:
                raise Exception('Analyze: Results for the same FB version required.')
        # step 2: Sort results into groups (platform, cpuarch, arch, run)
        results.sort(key=operator.attrgetter('platform','cpuarch','arch','sequence'))

        # pass 1: Create list of tests with results
        tests = {} # Dictionary of all tests found in results; Test ID: list of results
        for result in results:
            column = results.index(result)
            for test_id,test_result in result.items():
                tests.setdefault(test_id,len(results)*[None])[column] = test_result

        # pass 2: Analyze results for each tests that didn't pass in all runs
        test_details = {}
        # step 1: Collect details for tests that didn't pass
        for test_id,test_results in tests.items():
            for test_result in test_results:
                if test_result and test_result.outcome != Result.PASS:
                    l = test_details.setdefault(test_id,list())
                    result = results[test_results.index(test_result)]
                    l.append((self.get_run_tag(result.platform,result.cpuarch,result.arch,result.sequence),test_result))
        # step 2: group results for each test
        for test_id,test_results in test_details.items():
            groups = []  # item format: (result,[list_of_runs])
            for result_id,test_result in test_results:
                added = False
                for group in groups:
                    if self.compare_results(group[0],test_result):
                        group[1].append(result_id)
                        added = True
                if not added:
                    groups.append((test_result,[result_id]))
            del test_results[:]
            test_results.extend(groups)

        # pass 3: Order tests
        test_order = tests.keys()
        test_order.sort(key=okey)

        # pass 4: Generate report
        self.print_analysis(version,results,tests,test_details,test_order,
                            output_dir, diffs_only)
    def get_svn_login(self,realm, username, may_save):
        """Get Subversion login credentials from user.
        """
        if not username:
            username = raw_input("SVN User name:")
        else:
            print("SVN repository: ",realm)
            print("User: ",username)
        password = raw_input("Password:")
        retcode = True if username else False
        return retcode, username, password, True
    def svn_notify(self,event):
        """Notification callback from pysvn.
        """
        #  pysvn.wc_notify_action.update_completed
        if event['action'] == pysvn.wc_notify_action.update_completed:
            revision = event['revision']
            self.revision = revision
    def cmd_update_results(self,options):
        """Called by :func:`~fbtest.run_update` for command execution.
        """
        filenames = []

        if options.name:
            if os.path.isdir(options.name):
                filenames = self.get_result_filenames(options.name)
            elif os.path.isfile(options.name):
                filenames.append(options.name)
        else:
            filenames = self.get_result_filenames(os.getcwd())

        for filename in filenames:
            if not (options.arch or options.sequence or options.person):
                print("No update option specified.")
                print("For list of available options run: fbt_update result --help")
                return
            print ("Updating: %s" % filename)
            result = RunResults.load(filename)

            if options.arch:
                result.arch = options.arch
                result.dump(filename)
            if options.sequence:
                result.sequence = options.sequence
                result.dump(filename)
            if options.person:
                result.person_name = options.person.lower()
                result.person_id = options.person.upper()[:2]
                result.dump(filename)
    def cmd_update_repository(self,options):
        """Called by :func:`~fbtest.run_update` for command execution.
        """
        if pysvn_present:
            root_dir = os.getcwd()
            directories = ['fbk','fdb','files','resources','tests']
            svn = pysvn.Client()
            svn.callback_get_login = self.get_svn_login
            svn.callback_notify = self.svn_notify
            for directory in directories:
                path = os.path.join(root_dir,directory)
                if not os.path.exists(path):
                    # Fresh checkout
                    print("Checkout: ",directory)
                    svn.checkout(svn_repository+directory,
                                 path)
                else:
                    # Update
                    print("Update: ",directory)
                    svn.update(path)
            print('Revision:', self.revision.number)
        else:
            print ("pysvn module not installed. You can download it from http://pysvn.tigris.org/")


    def run_analyze(self,options):
        """Called by :func:`~fbtest.run_analyze` for command execution.
        """
        filenames = []

        if options.name:
            output_dir = os.getcwd()
            if os.path.isdir(options.name):
                filenames = self.get_result_filenames(options.name)
            elif os.path.isfile(options.name):
                filenames.append(options.name)
        else:
            output_dir = os.getcwd()
            filenames = self.get_result_filenames(os.getcwd())

        if options.output:
            output_dir = options.output

        self.analyze(filenames,output_dir,options.diffs_only)
    def run_view(self,options):
        """Called by :func:`~fbtest.run_view` for command execution.
        """
        filenames = []

        if options.name:
            if os.path.isdir(options.name):
                filenames = self.get_result_filenames(options.name)
            elif os.path.isfile(options.name):
                filenames.append(options.name)
        else:
            filenames = self.get_result_filenames(os.getcwd())

        for filename in filenames:
            result = RunResults.load(filename)
            if options.xunit:
                result.save_xunit(os.path.splitext(filename)[0]+'.xml')
            else:
                self.print_result_info(result,filename)
                self.print_fails(result,options.cause,options.details)
                self.print_errors(result,options.cause,options.details)
                self.print_untested(result,options.cause)
                print('')
    def cmd_archive_list(self,options):
        """Called by :func:`~fbtest.run_archive` for command execution.
        """
        repository = self.get_repository(options)
        print ("Files in archive:")
        print ()
        groups = (os.path.split(x) for x in repository.result_archive.list_filenames())
        groups2 = itertools.groupby(groups,operator.itemgetter(0))
        groups3 = ((k,[x[1] for x in g]) for k,g in groups2)
        for (version, filenames) in groups3:
            print ('%s:' % version)
            for filename in filenames:
                print ('   %s' % filename)
    def cmd_archive_save(self,options):
        """Called by :func:`~fbtest.run_archive` for command execution.
        """
        repository = self.get_repository(options)
        name = options.name if options.name else 'results.trf'
        try:
            last_results = RunResults.load(name)
            repository.result_archive.store(last_results)
            print("Results file '%s' stored into archive as '%s'" %
                  (os.path.basename(last_results.filename),
                   os.path.relpath(repository.result_archive.get_archive_file_path(last_results),
                                   repository.result_archive.archive_path)))
        except Exception as e:
            print(e)
    def cmd_archive_retrieve(self,options):
        """Called by :func:`~fbtest.run_archive` for command execution.
        """
        repository = self.get_repository(options)

        if options.current:
            if options.remote:
                runner = self.remote_fbtest.root.get_runner()
            else:
                runner = Runner(repository)
                runner.set_target('SS','localhost')
            version = runner.version
            print ('Current version:',version)
        elif options.version:
            version = options.version
        else:
            print ("Firebird version not specified.")
            print ("Use either '--version' or '--current' to specify it.")
            return

        results = repository.result_archive.retrieve(version)
        for result in results:
            if options.arch and options.arch != result.arch:
                continue
            if options.person and options.person.lower() != result.person_name:
                continue
            if options.sequence and options.sequence != result.sequence:
                continue
            filename = repository.result_archive.get_archive_filename(result)
            result.dump(os.path.join(options.output,filename))
            print (filename,'retrieved.')
    def cmd_archive_delete(self,options):
        """Called by :func:`~fbtest.run_archive` for command execution.
        """
        repository = self.get_repository(options)

        if options.current:
            if options.remote:
                runner = self.remote_fbtest.root.get_runner()
            else:
                runner = Runner(repository)
                runner.set_target('SS','localhost')
            version = runner.version
            print ('Current version:',version)
        elif options.version:
            version = options.version
        else:
            print ("Firebird version not specified.")
            print ("Use either '--version' or '--current' to specify it.")
            return

        results = repository.result_archive.retrieve(version)
        for result in results:
            if options.arch and options.arch != result.arch:
                continue
            if options.person and options.person.lower() != result.person_name:
                continue
            if options.sequence and options.sequence != result.sequence:
                continue
            repository.result_archive.delete(result)
            filename = repository.result_archive.get_archive_filename(result)
            print (filename,'deleted.')

#: :class:`ScriptRunner` instance.
script_runner = ScriptRunner()

def run_tests():
    """CLI Script function for test execution.

    This is a 'main' function called by :command:`fbt_run` script.
    Runs all tests in test reporsitory or specified test/suite. Result from
    test run is stored in current directory:

    :file:`results.trf` : Pickled :class:`RunResults` instance.
    Pickled :class:`RunResults` instance is also stored in 'archive'.

    :file:`results.xml` : XUNIT XML report (when -x or --xunit is specified).

    usage: fbt_run [options] [suite_or_test_name]

    .. program:: fbt_run

    .. option:: -v, --verbose

       Be more verbose

    .. option:: --verbosity=NUM

       Set verbosity; `--verbosity=2` is the same as `-v`

    .. option:: -q, --quiet

       Be less verbose

    .. option:: -b <directory>, --bin-dir=<directory>

       Location of Firebird binary tools (like gbak etc.).

    .. option:: -d <directory>, --db-dir=<directory>

       Location for temporary databases used by tests.

    .. option:: -k <name_or_file>, --skip=<name_or_file>

       Suite or test name or name of file with suite/test names to skip.

    .. option:: --archive

       If specified, last run result file is copied to archive.

    .. option:: --rerun

       If specified, runs only tests that don't PASSed in last run.

    .. option:: --remote

       If specified, connects to remote fbtest server and runs specified tests on it.

    .. option:: -u, --update

       If specified, updates last run results with re-run results.

    .. option:: -w <password>, --password=<password>

       SYSDBA password. (`default 'masterkey'`)

    .. option:: -o <machine>, --host=<machine>

       Firebird or fbtest host machine identification. (`default 'localhost'`)

    .. option:: -p <person>, --person=<person>

       QA person name. First two letters are used as person ID.

    .. option:: -a <arch>, --arch=<arch>

       Firebird architecture ('SS', 'CS' or 'SC'). (`default 'SS' - SuperServer`)

    .. option:: -s <number>, --sequence=<number>

       Run sequence number. Important to disctinguish repeated runs af the same
       tests on single 'target'. Used by :command:`fbt_analyze`. (`default '1'`)

    .. option:: -x, --xunit

       Provides test results also in the standard XUnit XML format.
    """
    parser = ArgumentParser()
    parser.add_argument('name',nargs='?',default=None,help="Suite or test name")
    parser.add_argument('-b','--bin-dir',help="Directory where Firebird binaries tools are")
    parser.add_argument('-d','--db-dir',help="Directory to use for test databases")
    parser.add_argument('--archive',action='store_true',help="Save last run results to archive")
    parser.add_argument('--rerun',action='store_true',help="Run only tests that don't PASSed in last run")
    parser.add_argument('-v','--verbose',action='store_true',help="Be more verbose")
    parser.add_argument('--verbosity',type=int,choices=[0,1,2],default=1,help="Set verbosity; --verbosity=2 is the same as -v")
    parser.add_argument('-q','--quiet',action='store_true',help="Be less verbose")
    parser.add_argument('-x','--xunit',action='store_true',help="Provides test results also in the standard XUnit XML format")
    if rpyc_available:
        parser.add_argument('--remote',action='store_true',help="Connect to remote fbtest server")

    parser.add_argument('-u','--update',action='store_true',help="Update last run results with re-run results")
    parser.add_argument('-w','--password',help="SYSDBA password")
    parser.add_argument('-o','--host',help="Remote Firebird or fbtest host machine identification")
    parser.add_argument('-p','--person',help="QA person name")
    parser.add_argument('-a','--arch',help="Firebird architecture: SS, CS, SC, EM")
    parser.add_argument('-s','--sequence',type=int,help="Run sequence number for this target")
    parser.add_argument('-k','--skip',help="Suite or test name or name of file with suite/test names to skip")
    parser.set_defaults(rerun=False,update=False,server=False,register=False,
                        remote=False,host='localhost',password='masterkey',
                        sequence=1,arch='SS',person=UNKNOWN)

    script_runner.run_tests(parser.parse_args())

def run_server():
    """CLI Script function for test execution.

    This is a 'main' function called by :command:`fbt_server` script.

    usage: fbt_server [options]

    .. program:: fbt_server

    .. option:: -b <directory>, --bin-dir=<directory>

       Location of Firebird binary tools (like gbak etc.).

    .. option:: -d <directory>, --db-dir=<directory>

       Location for temporary databases used by tests.

    .. option:: -w <password>, --password=<password>

       SYSDBA password. (`default 'masterkey'`)

    .. option:: -o <machine>, --host=<machine>

       Firebird host machine identification. (`default 'localhost'`)

    .. option:: -p <person>, --person=<person>

       QA person name. First two letters are used as person ID.

    .. option:: -a <arch>, --arch=<arch>

       Firebird architecture ('SS', 'CS' or 'SC'). (`default 'SS' - SuperServer`)

    .. option:: --register

       If specified, automatically registers RPyC slave server.

    """

    if not rpyc_available:
        print('rpyc module not installed.')
        print('To instal rpyc from PyPI use: pip install rpyc')
        return

    parser = ArgumentParser()
    parser.add_argument('-b','--bin-dir',help="Directory where Firebird binaries tools are")
    parser.add_argument('-d','--db-dir',help="Directory to use for test databases")
    parser.add_argument('-w','--password',default='masterkey',help="SYSDBA password")
    parser.add_argument('-o','--host', default='localhost',help="Firebird host machine identification")
    parser.add_argument('-r','--register',action='store_true',help="Automatically register RPyC slave server")
    parser.add_argument('-p','--person', default=UNKNOWN,help="Firebird host machine identification")
    parser.add_argument('-a','--arch',help="Firebird architecture: SS, CS, SC")
    parser.set_defaults(server=False,register=False,arch='SS')

    script_runner.run_server(parser.parse_args())

def run_analyze():
    """CLI Script function for test analysis.

    This is a 'main' function called by :command:`fbt_analyze` script.
    Reads result file or all result files in specified directory and writes
    HTML report in current or specified directory.

    usage: fbt_analyze [options] <file_or_directory>

    .. program:: fbt_analyze

    .. option:: -o <directory>, --output=<directory>

       Location where HTML report should be stored.

    .. option:: -d, --difs-only

       Show only diffs on detail pages.
    """

    parser = ArgumentParser()
    parser.add_argument('name',nargs='?',default=None,help="Results file or directory with result files")
    parser.add_argument('-o','--output',help="Analysis output directory")
    parser.add_argument('-d','--diffs-only',action='store_true',help="Show only diffs on detail pages")
    parser.set_defaults(output='',diffs_only=False)

    script_runner.run_analyze(parser.parse_args())

def run_update():
    """CLI Script function to update metadata in Result file(s).

    This is a 'main' function called by :command:`fbt_update` script.
    Reads result file or all result files in specified directory and updates
    metadata with specified value(s).

    usage::

       fbt_update {result,repository} [options]

       result             Change result file metadata.
       repository         Update Test Repository.

    .. program:: fbt_update

    Options for `fbt_update result`:

    .. option:: name

       Results file or directory with result files.

    .. option:: -a <arch>, --arch=<arch>

       Firebird architecture ('SS', 'CS' or 'SC').

    .. option:: -p <person>, --person=<person>

       QA person name. First two letters are used as person ID.

    .. option:: -s <number>, --sequence=<number>

       Run sequence number. Important to disctinguish repeated runs of the same
       tests on single 'target'. Used by :command:`fbt_analyze`.

    Options for `fbt_update repository`:

       None.
    """
    parser = ArgumentParser()
    subparsers = parser.add_subparsers(title="Commands",
                                       help="Use <command> --help for more information about command.")

    parser_result = subparsers.add_parser('result',
                                          description="Changes metadata of result file(s).",
                                          help="Change result file metadata.")
    parser_result.add_argument('name',nargs='?',default=None,help="Results file or directory with result files")
    parser_result.add_argument('-a','--arch',help="Update result(s): set ARCH")
    parser_result.add_argument('-p','--person',help="Update result(s): set PERSON")
    parser_result.add_argument('-s','--sequence',type=int,help="Update result(s): set SEQUENCE NUMBER")
    parser_result.set_defaults(func=script_runner.cmd_update_results)

    parser_repository = subparsers.add_parser('repository',
                                              description="Update local test repository from Firebird project Subversion repository.",
                                              help="Update test repository.")
    parser_repository.set_defaults(func=script_runner.cmd_update_repository)

    args = parser.parse_args()
    args.func(args)


def run_view():
    """CLI Script function to update metadata in Result file(s).

    This is a 'main' function called by :command:`fbt_view` script.
    Reads result file or all result files in specified directory and prints
    information about stored results.

    usage: fbt_view <file_or_directory>

    .. program:: fbt_view

    .. option:: -x, --xunit

       Store processed test results in the standard XUnit XML format.

    .. option:: -c, --cause

       Print cause of fails and errors.

    .. option:: -d, --details

       Print details for fails and errors.

    """
    parser = ArgumentParser()
    parser.add_argument('name',nargs='?',default=None,help="Results file or directory with result files")
    parser.add_argument('-x','--xunit',action='store_true',help="Save test results in the standard XUnit XML format")
    parser.add_argument('-c','--cause',action='store_true',help="Print cause of fails and errors.")
    parser.add_argument('-d','--details',action='store_true',help="Print details for fails and errors.")
    #parser.add_argument('-o','--output',matavar='FILENAME',help="Save output to file.")

    script_runner.run_view(parser.parse_args())

def run_archive():
    """CLI Script function to maintain archive of Result file(s).

    This is a 'main' function called by :command:`fbt_archive` script.

    usage::

       fbt_update {list,save,retrieve,delete} [options]

       list                List result(s) in archive.
       save                Save result(s) to archive.
       retrieve            Retrieve result(s) from archive.
       delete              Delete result(s) from archive.

    .. program:: fbt_archive

    .. option:: --remote

       If specified, connects to remote fbtest server (and archive).

    .. option:: -o <machine>, --host=<machine>

       Remote fbtest host machine identification. (`default 'localhost'`)

    Options for `fbt_archive list`:

       None.

    Options for `fbt_archive save`:

    .. option:: name

       Results file.

    Options for `fbt_archive retrieve`:

    .. option:: -v <version_number>, --version=<version_number>

       Retrieve results only for specified Firebird version.

    .. option:: -c, --current

       Retrieve results only for currently tested Firebird version.

    .. option:: -o <directory>, --output=<directory>

       Location where result file(s) should be copied.

    .. option:: -p <person>, --person=<person>

       Retrieve results only for specified QA person name. First two letters are used as person ID.

    .. option:: -a <arch>, --arch=<arch>

       Retrieve results only for specified Firebird architecture ('SS', 'CS' or 'SC').

    .. option:: -s <number>, --sequence=<number>

       Retrieve results only for specified run sequence number.

    Options for `fbt_archive delete`:

    .. option:: -v <version_number>, --version=<version_number>

       Delete results only for specified Firebird version.

    .. option:: -c, --current

       Delete results only for currently tested Firebird version.

    .. option:: -p <person>, --person=<person>

       Delete results only for specified QA person name. First two letters are used as person ID.

    .. option:: -a <arch>, --arch=<arch>

       Delete results only for specified Firebird architecture ('SS', 'CS' or 'SC').

    .. option:: -s <number>, --sequence=<number>

       Delete results only for specified run sequence number.

    """
    parser = ArgumentParser()
    if rpyc_available:
        parser.add_argument('--remote',default=False,action='store_true',
                            help="Connect to remote fbtest server")
        parser.add_argument('-o','--host', default='localhost',
                            help="Remote fbtest host machine identification")

    subparsers = parser.add_subparsers(title="Commands",
                                       help="Use <command> --help for more information about command.")

    parser_list = subparsers.add_parser('list',
                                        description="List result(s) in archive.",
                                        help="List result(s) in archive.")
    parser_list.set_defaults(func=script_runner.cmd_archive_list)

    parser_save = subparsers.add_parser('save',
                                        description="Save result(s) to archive.",
                                        help="Save result(s) to archive.")
    parser_save.add_argument('name',nargs='?',default=None,help="Results file")
    parser_save.set_defaults(func=script_runner.cmd_archive_save)

    parser_retrieve = subparsers.add_parser('retrieve',
                                            description="Retrieve result(s) from archive.",
                                            help="Retrieve result(s) from archive.")
    parser_retrieve.add_argument('-v','--version',
                                 help="Only specified Firebird version")
    parser_retrieve.add_argument('-c','--current',action='store_true',
                                 help="Only currently tested Firebird version")
    parser_retrieve.add_argument('-o','--output',help="Output directory")
    parser_retrieve.add_argument('-a','--arch',
                                 help="Firebird architecture: SS, CS, SC")
    parser_retrieve.add_argument('-p','--person',help="QA person name")
    parser_retrieve.add_argument('-s','--sequence',type=int,
                                 help="Run sequence number")
    parser_retrieve.set_defaults(current=False,version='',output=os.getcwd(),
                                 func=script_runner.cmd_archive_retrieve)

    parser_delete = subparsers.add_parser('delete',
                                          description="Delete result(s) from archive.",
                                          help="Delete result(s) from archive.")
    parser_delete.add_argument('-v','--version',
                               help="Only specified Firebird version")
    parser_delete.add_argument('-c','--current',action='store_true',
                               help="Only currently tested Firebird version")
    parser_delete.add_argument('-a','--arch',
                               help="Firebird architecture: SS, CS, SC")
    parser_delete.add_argument('-p','--person',help="QA person name")
    parser_delete.add_argument('-s','--sequence',type=int,
                               help="Run sequence number")
    parser_delete.set_defaults(current=False,version='',
                               func=script_runner.cmd_archive_delete)
    args = parser.parse_args()
    args.func(args)

if __name__=='__main__':
    run_tests()
