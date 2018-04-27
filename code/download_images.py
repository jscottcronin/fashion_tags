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


def parse_dataset(_dataset, _outdir, _max=50000, _sample_size=None):
    """
    parse the dataset to create a list of tuple containing absolute path and url of image
    :param _dataset: dataset to parse
    :param _outdir: output directory where data will be saved
    :param _max: maximum images to download (change to download all dataset)
    :return: list of tuple containing absolute path and url of image
    """
    _fnames_urls = []
    with open(_dataset, 'r') as f:
        data = json.load(f)
        for image in data["images"]:
            url = image["url"]
            fname = os.path.join(outdir, "{}.jpg".format(image["imageId"]))
            _fnames_urls.append((fname, url))
    if _sample_size is not None and _sample_size > 0 and _sample_size <= _max and _sample_size <= len(_fnames_urls):
        _fnames_urls = pd.DataFrame(_fnames_urls).sample(_sample_size).values.tolist()
    return _fnames_urls[:_max]


if __name__ == '__main__':   
    
    if len(sys.argv) < 3:
        print("error: not enough arguments")
        sys.exit(0)

    # get args and create output directory
    dataset = sys.argv[1]
    outdir = sys.argv[2]
    try:
        sample_size = int(sys.argv[3])
    except IndexError:
        sample_size = None
    
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    # parse json dataset file
    fnames_urls = parse_dataset(dataset, outdir, _sample_size=sample_size)
    
    # download data
    pool = multiprocessing.Pool(processes=12)
    with tqdm(total=len(fnames_urls)) as progress_bar:
        for _ in pool.imap_unordered(download_image, fnames_urls):
            progress_bar.update(1)

    sys.exit(1)