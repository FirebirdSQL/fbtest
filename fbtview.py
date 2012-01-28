#!/usr/bin/python
#
#   PROGRAM/MODULE: 
#   FILE:           fbtview.py
#   DESCRIPTION:    Firebird QA system
#   CREATED:        15.2.2011
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
#  Copyright (c) 2011 Pavel Cisar <pcisar@users.sourceforge.net>
#  and all contributors signed below.
#
#  All Rights Reserved.
#  Contributor(s): ______________________________________.

import os
import operator
from fbtest import *
from mako.template import Template
from mako.lookup import TemplateLookup
from itertools import groupby

makolookup = TemplateLookup(directories=['templates'], output_encoding='utf-8', encoding_errors='replace')

def run_tag(platform,cpuarch,arch,sequence):
    return '%s%s%s%i' % (platform.lower()[:1],cpuarch,arch.lower(),sequence)

def print_result_info(result):
    print 'File:     %s' % filename
    print 'Desc:     %s' % result.description
    print 'Version:  %s' % result.version
    print 'Arch:     %s' % result.arch
    print 'Platform: %s' % result.platform
    print 'CPU:      %s' % result.cpuarch
    if hasattr(result,'sequence'):
        print 'Sequence: %s' % result.sequence
    print 'Person:   %s (%s)' % (result.person_name,result.person_id)
    result.printSummary()
    print

def print_fails(result):
    fails = result.get_fails()
    if fails:
        print '--- FAILS '+('-'*60)
    for fail in fails:
        print fail.id
        #print fail.get_cause()
        #for (kind, annotation) in fail.annotations.items():
            #if 'cause' in kind:
                #print '%s:\n%s\n' % (kind, as_utf8(annotation))

def print_errors(result):
    errors = result.get_errors()
    if errors:
        print '--- ERRORS '+('-'*59)
    for error in errors:
        print error.id

def print_analysis(version,results,tests,test_details,test_order,output_dir):
    def format_result(r):
        return '%s %s' % (r.outcome,r.get_cause())
    
    main_template = makolookup.get_template("main.mako")
    detail_template = makolookup.get_template("detail.mako")
    
    #for result in results:
        #print '%i: %s %s %s %i' % (results.index(result)+1,result.platform,result.cpuarch,result.arch,result.sequence)

    #for test_id,test_results in tests.items():
        #print '%-70s' % (test_id),
        #for test_result in test_results:
            #if test_result:
                #print '%-6s' % test_result.outcome,
            #else:
                #print '%-6s' % 'N/A'
        #print
    
    #print '--- DETAILS '+('-'*58)
    #for test_id,test_detail in test_details.items():
        #print test_id
        #for group in test_detail:
            #print format_result(group[0]),'('+','.join(group[1])+')'
        #print ('-'*70)
    
    f = open(os.path.join(output_dir,'index.html'),'w')
    try:
        f.write(main_template.render(version=version,results=results,tests=tests,
                               test_details=test_details,test_order=test_order))
    finally:
        f.close()

    for test_id,test_detail in test_details.items():
        #print 'Detail: ',test_id
        f = open(os.path.join(output_dir,test_id+'.html'),'w')
        try:
            f.write(detail_template.render(version=version,test_id=test_id,
                                   test_detail=test_detail))
        finally:
            f.close()

def compare_results(r1,r2):
    result = (r1.kind == r2.kind) and (r1.outcome == r2.outcome)
    if result:
        result = reduce(lambda x,y: x and y,map(lambda x,y: x == y,r1.annotations.items(),r2.annotations.items()))
    return result
    
def analyze(filenames,output_dir):
    def okey(value):
        r = max((['PASS', 'ERROR', 'FAIL', 'UNTESTED'].index(r.outcome) for r in tests[value] if r))
        if r == 0:
            return value
        else:
            return r
        #return overall_outcome_weight(tests[value])
        #return ['PASS', 'ERROR', 'FAIL', 'UNTESTED'].index(r.outcome)
    def overall_outcome_weight(results):
        return max((['PASS', 'ERROR', 'FAIL', 'UNTESTED'].index(r.outcome) for r in results if r))
    
    # pass 0: Load results
    results = [RunResults.load(filename) for filename in filenames]
    # step 1: Check if all results are for the same version
    version = results[0].version
    for result in results:
        if result.version != version:
            raise Exception('Analyze: Results for the same FB version required.')
    # step 2: Rearange results in groups (platform, cpuarch, arch, run)
    platforms = {}
    for result in results:
        platform = platforms.setdefault(result.platform,dict())
        cpuarch = platform.setdefault(result.cpuarch,dict())
        arch = cpuarch.setdefault(result.arch,list())
        arch.append(result)
    new_results = []
    for platform in platforms.values():
        for cpuarch in platform.values():
            for arch in cpuarch.values():
                arch.sort(key=operator.attrgetter('sequence'))
                new_results.extend(arch)
    results = new_results
    
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
                l.append((run_tag(result.platform,result.cpuarch,result.arch,result.sequence),test_result))
    # step 2: group results for each test
    for test_id,test_results in test_details.items():
        groups = []  # item format: (result,[list_of_runs])
        for result_id,test_result in test_results:
            added = False
            for group in groups:
                if compare_results(group[0],test_result):
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
    print_analysis(version,results,tests,test_details,test_order,output_dir)

if __name__=='__main__':
    from optparse import OptionParser
    
    parser = OptionParser('usage: %prog [options] <file_or_directory>')
    parser.add_option('-a','--arch',help='Update result(s): set ARCH')
    parser.add_option('-p','--person',help='Update result(s): set PERSON')
    parser.add_option('-s','--sequence',type='int',help='Update result(s): set SEQUENCE NUMBER')
    parser.add_option('-o','--output',help='Analysis output directory')
    parser.add_option('--analyze',action='store_true',help='Analyze result(s).')
    parser.set_defaults(analyze=False,output='')
    
    (options,args) = parser.parse_args()
    if len(args) != 1:
        parser.error('incorrect number of arguments')
    
    filenames = []
    if os.path.isdir(args[0]):
        output_dir = args[0]
        dirlist = os.listdir(args[0])
        filenames = [os.path.join(args[0],name) for name in dirlist 
                              if os.path.isfile(os.path.join(args[0],name)) and 
                              os.path.splitext(name)[1].lower() == '.trf']
    else:
        output_dir = os.getcwd()
        filenames.append(args[0])
    
    if options.analyze:
        analyze(filenames,output_dir)
    else:
        for filename in filenames:
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
            
            print_result_info(result)
            print_fails(result)
            print_errors(result)
            print
