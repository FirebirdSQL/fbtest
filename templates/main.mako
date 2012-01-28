<%inherit file="base.mako"/>
<%
from operator import attrgetter
from itertools import groupby

platforms = [(k,len(list(g))) for k,g in groupby(results,attrgetter('platform'))]
cpuarchs = [(k,len(list(g))) for k,g in groupby(results,attrgetter('cpuarch'))]
archs = [(k,len(list(g))) for k,g in groupby(results,attrgetter('arch'))]
runs = [(k,len(list(g))) for k,g in groupby(results,attrgetter('sequence'))]

%>
<table width="100%" border=1>
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
