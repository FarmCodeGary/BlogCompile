<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0">
<channel>
        <title>${siteTitle}</title>
        <description>${siteDescription}</description>
        <link>${remoteUrl}</link>

% for post in blogPosts:
        <item>
                <title>${post.title}: ${post.teaser}</title>
                <description>${post.body}</description>
                <link>${remoteUrl}/${post.outputPath}</link>
                <guid>${post.guid}</guid>
                <pubDate>${post.postedRssDateTime}</pubDate>
        </item>
% endfor
 
</channel>
</rss>

