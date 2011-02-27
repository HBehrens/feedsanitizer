from django.utils.feedgenerator import RssFeed, rfc2822_date

#slighty modified version to simplyfy author tag
class Rss201rev2FeedModified(RssFeed):
    # Spec: http://blogs.law.harvard.edu/tech/rss
    _version = u"2.0"
    def add_item_elements(self, handler, item):
        handler.addQuickElement(u"title", item['title'])
        handler.addQuickElement(u"link", item['link'])
        if item['description'] is not None:
            handler.addQuickElement(u"description", item['description'])

        # Author information.
        if item["author_name"] and item["author_email"]:
            handler.addQuickElement(u"author", "%s (%s)" % \
                (item['author_email'], item['author_name']))
        elif item["author_email"]:
            handler.addQuickElement(u"author", item["author_email"])
        elif item["author_name"]:
            #handler.addQuickElement(u"dc:creator", item["author_name"], {u"xmlns:dc": u"http://purl.org/dc/elements/1.1/"})
            handler.addQuickElement(u"author", item["author_name"])

        if item['pubdate'] is not None:
            handler.addQuickElement(u"pubDate", rfc2822_date(item['pubdate']).decode('utf-8'))
        if item['comments'] is not None:
            handler.addQuickElement(u"comments", item['comments'])
        if item['unique_id'] is not None:
            handler.addQuickElement(u"guid", item['unique_id'])
        if item['ttl'] is not None:
            handler.addQuickElement(u"ttl", item['ttl'])

        # Enclosure.
        if item['enclosure'] is not None:
            handler.addQuickElement(u"enclosure", '',
                {u"url": item['enclosure'].url, u"length": item['enclosure'].length,
                    u"type": item['enclosure'].mime_type})

        # Categories.
        for cat in item['categories']:
            handler.addQuickElement(u"category", cat)