'''

Copyright (c) 2017 Vanessa Sochat

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

'''

from django.core.files import File
from django.http.response import Http404
from sendit.apps.main.models import (
    Image,
    Batch
)

from sendit.logger import bot
import sys
import os


#### GETS #############################################################

def get_batch(sid):
    '''get a single report, or return 404'''
    keyargs = {'id':sid}
    try:
        batch = Batch.objects.get(**keyargs)
    except Batch.DoesNotExist:
        raise Http404
    else:
        return batch


def get_image(sid):
    '''get a single report, or return 404'''
    keyargs = {'id':sid}
    try:
        image = Image.objects.get(**keyargs)
    except Image.DoesNotExist:
        raise Http404
    else:
        return image


def ls_fullpath(dirname,ext=None):
    '''get full path of all files in a directory'''
    if ext is not None:
        return [os.path.join(dirname, f) for f in os.listdir(dirname) if f.endswith(ext)]
    return [os.path.join(dirname, f) for f in os.listdir(dirname)]





#### WORKER ##########################################################

def start_tasks(count=1, base='/data')
    '''
    submit some count of tasks based on those that aren't present
    as batches

    Parameters
    ==========
    count: the number to submit. Default is 1
    base: the base data folder, defaults to /data
    '''
    from sendit.apps.main.tasks import import_dicomdir
    current = [x.uid for x in Batch.objects.all()]
    contenders = get_contenders(base=base,current=current)

    # We can't return more contenders than are available
    if count > len(contenders):
       count = len(contenders) - 1

    contenders = contenders[0:count]
    bot.debug("Starting deid pipeline for %s folders" %len(contenders))
    for contender in contenders:
        dicom_dir = "%s/%s" %(base,contender)
        import_dicomdir.apply_async(kwargs={"dicom_dir":dicom_dir})


def get_contenders(base,current=None):
    contenders = [x for x in os.listdir(base) if not os.path.isdir(x)]
    contenders = [x for x in contenders if not x.endswith('tmp')]
    if current is not None:
        contenders = [x for x in contenders if x not in current]
    return contenders
