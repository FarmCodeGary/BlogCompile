<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0">
<channel>
        <title>${site_title}</title>
        <description>${site_description}</description>
        <link>${remote_url}</link>

% for post in blog_posts:
        <item>
                <title>${post.title}: ${post.teaser}</title>
                <description>${post.body}</description>
                <link>${remote_url}/${post.output_path}</link>
                <guid>${post.guid}</guid>
                <pubDate>${post.posted_rss_datetime}</pubDate>
        </item>
% endfor

</channel>
</rss>
