<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>${doc.title} (${siteTitle})</title>
<%include file="headerlinks.makoscrap"/>
</head>
<body>
<%include file="siteheader.makoscrap"/>
${doc.header}
${doc.html_title}
${doc.html_subtitle}
${doc.docinfo}
<hr/>
<article>
${doc.body}
</article>
${doc.footer}

% if remote:
<hr/>
<div id="disqus_thread"></div>
<script type="text/javascript">
    var disqus_shortname = '${disqusShortname}';
    var disqus_identifier = '${doc.guid}';
    var disqus_url = '${remoteUrl}/${doc.outputPath}';
    var disqus_title = '${doc.title}';    

    /* * * DON'T EDIT BELOW THIS LINE * * */
    (function() {
        var dsq = document.createElement('script'); dsq.type = 'text/javascript'; dsq.async = true;
        dsq.src = 'http://' + disqus_shortname + '.disqus.com/embed.js';
        (document.getElementsByTagName('head')[0] || document.getElementsByTagName('body')[0]).appendChild(dsq);
    })();
</script>
<noscript>Please enable JavaScript to view the comments powered by <a href="http://disqus.com/?ref_noscript">Disqus</a>.</noscript>
% endif
<%include file="sitefooter.makoscrap"/>
</body>
</html>
