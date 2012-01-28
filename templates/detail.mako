<%inherit file="base.mako"/>\
<H1>Details for test ${test_id}</H1>
%for group in test_detail:
<% 
result = group[0]
i = 1
%>
<H2>${', '.join(group[1])}</H2>
<table width="100%" border=1>
<tr><th>Annotation</th><th>Value</th></tr>
<tr><td class="cause">Cause</td><td class="cause">${result.get_cause()}</td></tr>
%for key,value in ((x,y) for x,y in result.annotations.items() if x != result.CAUSE):
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