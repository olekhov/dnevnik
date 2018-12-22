#!env python3

import json
from MESHDownloader import DownloadCM

from pprint import pprint

with open('book.json') as f:
    data = json.load(f)

pprint(data, depth=2, compact=True)

#pprint(data['articles'], depth=3, compact=True)

DownloadCM(data)


