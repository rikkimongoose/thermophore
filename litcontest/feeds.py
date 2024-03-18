from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import Atom1Feed
from .models import Contest
from .utils import is_blank, make_url

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
        finishes_date = item.finishes.strftime(DATE_FORMAT)
        theme = f"Тема от: {item.theme_by} — {item.theme}" if is_blank(item.theme) else ''
        return f"{item.title}.{theme}. Объявление темы: {starts_date}. Окончание приёма работ {finishes_date}"

    def item_link(self, item):
        return make_url(RSS_LINK, "/contest", f"/{item.id}")

    def item_pubdate(self, item):
        return item.starts.strftime(DATE_FORMAT)

class AtomSiteNewsFeed(RssSiteNewsFeed):
    feed_type = Atom1Feed
    subtitle = RssSiteNewsFeed.description