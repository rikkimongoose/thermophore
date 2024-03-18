import datetime
import io
from .models import Contest
from zipfile import ZipFile

from urllib.parse import urlencode

START_TIME = '15:00'

def date_to_datetime(date):
    time = datetime.datetime.strptime(START_TIME,'%H:%M').time()
    return datetime.datetime.combine(date, time)

def is_blank(text):
    return not (text and text.strip())

def update_groups(contest_id):
    if Story.objects.filter(contest__id = contest_id, group__isnull = False).exists():
        return
    max_in_group = Contest.objects.filter(id = contest_id).only('max_in_group')
    stories = Story.objects.filter(contest__id = contest_id).only('group')
    stories_len = len(stories)
    group_index = max_in_group // stories_len
    stories_id = map(lambda s: s.id, stories) 
    stories_dict = {}
    for i in range(stories_len):
        stories_dict[stories_id[i]] = i % group_index
    with transaction.atomic():
        for key, group in stories_dict:
            User.objects.filter(id=key).update(group=group)

def pack_to_zip(files_dict):
    zip_buffer = io.BytesIO()
    with ZipFile(zip_buffer, "a", ipfile.ZIP_DEFLATED, False) as zip_file:
        for file_name, text in files_dict:
            zip_file.writestr(file_name, text.getvalue())
    zip_buffer.seek(0)
    return zip_buffer

def make_url(base_url, *uris):
    url = base_url.rstrip('/')
    for uri in uris:
        _uri = uri.strip('/')
        url = '{}/{}'.format(url, _uri) if _uri else url
    return url