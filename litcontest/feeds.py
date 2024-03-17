from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import Atom1Feed
from .models import Contest
from .utils import isBlank

RSS_LINK = 'http://thermophore.ru/'
DATE_FORMAT = '%Y-%m-%d'

class RssSiteNewsFeed(Feed):
    title = 'Новый конкурсный движок'
    link = RSS_LINK
    description = 'Recent items in the competitions drive.'
    def items(self):
        return Contest.objects.order_by('-starts')[:10]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        starts_date = item.starts.strftime(DATE_FORMAT)
        finishes_date = item.finishess.strftime(DATE_FORMAT)
        theme = ' Тема от: %s - %s' % (item.theme_by, item.theme) if isBlank(item.theme) else ''
        return '%s.%s. Объявление темы: %s. Окончание приёма работ %s' % (item.title, theme, starts_date, finishes_date)

    def item_link(self, item):
        return item.description

    def item_guid(self, item):
        return "%scontest/%s" % (RSS_LINK, item.id)

    def item_pubdate(self, item):
        return item.starts.strftime(DATE_FORMAT)

class AtomSiteNewsFeed(RssSiteNewsFeed):
    feed_type = Atom1Feed
    subtitle = RssSiteNewsFeed.description