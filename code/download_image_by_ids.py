# Download images using csv of ids:
# python download_image_by_ids.py ~/data/iMaterialist/train.json ~/data/iMaterialist/train_30k ~/data/iMaterialist/train_30k_labels.csv

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


def load_dataset(_dataset, _outdir, _filter_ids):
    with open(_dataset, 'r') as f:
        data_dict = json.load(f)

    imgs = pd.DataFrame(data_dict['images'])
    imgs.columns = ['id', 'url']
    imgs['fn'] = _outdir + imgs['id'] + '.jpg'
    imgs = imgs.loc[imgs['id'].isin(_filter_ids), :]
    return imgs


def format_urls_for_download(_data_df):
    _fnames_urls = _data_df[['fn', 'url']].values.tolist()
    return _fnames_urls


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
    train_json = sys.argv[1]
    outdir = sys.argv[2]
    if not outdir.endswith('/'):
        outdir += '/'

    labels = pd.read_csv(sys.argv[3], dtype=str)
    filter_ids = labels['id'].unique()
    
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    # load dataset as dataframe
    df = load_dataset(train_json, outdir, filter_ids)
    
    # format id and urls for threading image downloads
    fnames_urls = format_urls_for_download(df)
    
    # download data
    pool = multiprocessing.Pool(processes=12)
    with tqdm(total=len(fnames_urls)) as progress_bar:
        for _ in pool.imap_unordered(download_image, fnames_urls):
            progress_bar.update(1)

    sys.exit(1)