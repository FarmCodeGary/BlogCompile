<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>${siteTitle}</title>
<%include file="headerlinks.makoscrap"/>
</head>

<body>
<%include file="siteheader.makoscrap"/>

${doc.body}

<h2>Latest Posts:</h2>
% for post in blogPosts[:9]:
<div class="postpreview">
<p class="postinfo">${post.postedDateVerbose}:</p>
<h3><a href="${rootUrl}/${post.outputPath}">${post.title}</a></h3>
<p class="postteaser">${post.teaser}</p>
</div>
% endfor
<h3><a href="${rootUrl}/blog/blog-index.html">(more...)</a></h3>

${doc.footer}

<%include file="sitefooter.makoscrap"/>
</body>
</html>

