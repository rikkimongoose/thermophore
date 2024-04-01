import datetime
import io
from .models import Contest, Story
from zipfile import ZipFile, ZIP_DEFLATED

from urllib.parse import urlencode

START_TIME = '15:00'

def date_to_datetime(date):
    time = datetime.datetime.strptime(START_TIME,'%H:%M').time()
    return datetime.datetime.combine(date, time)

def is_blank(text):
    return not (text and text.strip())

def update_groups(contest_id):
    if Story.objects.filter(Q(contest__id = contest_id) & Q(group__isnull = False)).exists():
        return
    max_in_group = Contest.objects.filter(id = contest_id).only('max_in_group')
    stories = Story.objects.filter(contest__id = contest_id)
    for i in range(len(stories)):
        stories[i].group = i // max_in_group
    Story.objects.bulk_update(stories, ["group"])

def pack_to_zip(files_dict):
    zip_buffer = io.BytesIO()
    zip_file = ZipFile(zip_buffer, 'w')
    for file_name in files_dict:
        zip_file.writestr(file_name, files_dict[file_name])
    zip_file.close()
    return zip_buffer.getvalue()

def make_url(base_url, *uris):
    url = base_url.rstrip('/')
    for uri in uris:
        _uri = uri.strip('/')
        url = '{}/{}'.format(url, _uri) if _uri else url
    return url