<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>${site_title}</title>
<%include file="headerlinks.makoscrap"/>
</head>

<body>
<%include file="siteheader.makoscrap"/>

${doc.body}

<h2>Latest Posts:</h2>
% for post in blog_posts[:9]:
<div class="postpreview">
<p class="postinfo">${post.posted_date_verbose}:</p>
<h3><a href="${root_url}/${post.output_path}">${post.title}</a></h3>
<p class="postteaser">${post.teaser}</p>
</div>
% endfor
<h3><a href="${root_url}/blog/blog-index.html">(more...)</a></h3>

${doc.footer}

<%include file="sitefooter.makoscrap"/>
</body>
</html>
