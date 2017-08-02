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

from sendit.logger import bot
from sendit.apps.main.models import (
    Batch,
    BatchIdentifiers,
    Image
)

from django.conf import settings
import os


def chunks(l, n):
    '''Yield successive n-sized chunks from l.'''
    for i in range(0, len(l), n):
        yield l[i:i + n]


### FILES ##############################################################

def save_image_dicom(dicom,dicom_file,basename=None):
    '''save image dicom will save a dicom file to django's media
    storage, for this application defined under /images.
    :param dicom: the main.Image instance 
    :param dicom_file: the dicom file (usually in /data) to save
    '''
    if basename is None:
        basename = os.path.basename(dicom_file)

    with open(dicom_file,'rb') as filey:
              django_file = File(filey)
              dicom.image.save(basename,
                               django_file,
                               save=True)  
    dicom.save()
    return dicom


## MODELS ##############################################################

def add_batch_error(message,batch):
    '''add batch error will log an error, and flag the batch to have it.
    '''
    bot.error(message)
    batch.has_error = True
    if "errors" not in batch.logs:
        batch.logs['errors'] = []
    # Only add the unique error once
    if message not in batch.logs['errors']:
        batch.logs['errors'].append(message)
    batch.status = 'ERROR'
    batch.save()
    return batch  


def change_status(images,status):
    '''change status will update an instance status
     to the status choice provided. This works for batch
    and images
    '''
    updated = []
    if not isinstance(images,list):
        images = [images]
    for image in images:
        image.status=status
        image.save()
        updated.append(image)
    if len(updated) == 1:
        updated = updated[0]
    return updated