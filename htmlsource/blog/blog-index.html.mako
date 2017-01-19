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
% for post in blog_posts:
<tr>
<td><a href="${root_url}/${post.output_path}">${post.title}</a></td>
<td>${post.posted_date_terse}</td>
</tr>
% endfor
</table>

<%include file="/sitefooter.makoscrap"/>

</body>
</html>

