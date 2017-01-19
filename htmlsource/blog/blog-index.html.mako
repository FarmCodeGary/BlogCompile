<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>All Posts (${site_title})</title>
<%include file="/headerlinks.makoscrap"/>
</head>

<body>
<%include file="/siteheader.makoscrap"/>

<h2>All Posts:</h2>

<table>
% for post in blogPosts:
<tr>
<td><a href="${rootUrl}/${post.outputPath}">${post.title}</a></td>
<td>${post.postedDateTerse}</td>
</tr>
% endfor
</table>

<%include file="/sitefooter.makoscrap"/>

</body>
</html>

