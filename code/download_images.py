# Download validation data:
# python download_images.py ~/data/iMaterialist/validation.json ~/data/iMaterialist/valid

# Download test data:
# python download_images.py ~/data/iMaterialist/test.json ~/data/iMaterialist/test

# Download 10k train data:
# python download_images.py ~/data/iMaterialist/train.json ~/data/iMaterialist/train_10k 10000


from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import io
import os
import sys
import json
import urllib3
import multiprocessing
import pandas as pd

from PIL import Image
from tqdm import tqdm
from urllib3.util import Retry

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def load_dataset(_dataset, _outdir):
    with open(_dataset, 'r') as f:
        data_dict = json.load(f)

    imgs = pd.DataFrame(data_dict['images'])
    imgs.columns = ['id', 'url']
    imgs['fn'] = _outdir + imgs['id'] + '.jpg'

    if 'annotations' in data_dict:
        labels = pd.DataFrame(data_dict['annotations'])
        labels.columns = ['id', 'label']
        labels['label'] = labels['label'].apply(lambda lst: ' '.join(lst))
        data_df = imgs.merge(labels, how='inner', on='id')
    else:
        data_df = imgs
    return data_df


def format_urls_for_download(_data_df, _max=50000):
    _fnames_urls = _data_df[['fn', 'url']].values.tolist()
    return _fnames_urls[:_max]


def download_image(fnames_and_urls):
    """
    download image and save its with 90% quality as JPG format
    skip image downloading if image already exists at given path
    :param fnames_and_urls: tuple containing absolute path and url of image
    """
    fname, url = fnames_and_urls
    if not os.path.exists(fname):
        http = urllib3.PoolManager(retries=Retry(connect=3, read=2, redirect=3))
        response = http.request("GET", url)
        image = Image.open(io.BytesIO(response.data))
        image_rgb = image.convert("RGB")
        image_rgb.save(fname, format='JPEG', quality=90)


if __name__ == '__main__':   
    
    if len(sys.argv) < 3:
        print("error: not enough arguments")
        sys.exit(0)

    # get args and create output directory
    dataset = sys.argv[1]
    outdir = sys.argv[2]
    if not outdir.endswith('/'):
        outdir += '/'
    
    try:
        sample_size = int(sys.argv[3])
    except IndexError:
        sample_size = None
    
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    # load dataset as dataframe
    df = load_dataset(dataset, outdir)
    
    # sample the dataset if desired
    if sample_size is not None:
        df = df.sample(sample_size)
    
    # store labels for imgs we are about to download if in train / validation
    if 'label' in df.columns:
        df[['id', 'label']].to_csv(f'{outdir[:-1]}_labels.csv', index=False)
    
    # format id and urls for threading image downloads
    fnames_urls = format_urls_for_download(df, _max=50000)
    
    # download data
    pool = multiprocessing.Pool(processes=12)
    with tqdm(total=len(fnames_urls)) as progress_bar:
        for _ in pool.imap_unordered(download_image, fnames_urls):
            progress_bar.update(1)

    sys.exit(1)