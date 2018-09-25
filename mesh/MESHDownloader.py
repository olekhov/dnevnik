#!env python3

import json
from pprint import pprint
from urllib.parse import unquote
from tqdm import tqdm
import os
import requests


""" Download composed_material """
def DownloadCM(js):

    site="https://uchebnik.mos.ru"

    print(f"Название: {js['name']}")
    print(f"Описание: {js['description']}")

    print(f"Разделов: {len(js['articles'])}")
    page=1

    pm=open("pdfmarks","w")
    gs=open("build_pdf.sh","w")

    gs.write("gs -dBATCH -dNOPAUSE -sDEVICE=pdfwrite -sOutputFile=fromgs.pdf -sPAPERSIZE=a4 viewjpeg.ps ./pdfmarks -c \"\\")

    pm.write(
f""" [ /Title <{TOHEX(js['name'])}> 
/Subject <{TOHEX(js['description'])}>
/Author <{TOHEX(js['user_name'])}>
/DOCINFO pdfmark
""")


    for aidx, a in enumerate(js['articles'], start=1):
        print(f"{aidx:02}. {a['name']}")
        pm.write(f"[ /Title <{TOHEX(str(aidx)+'. '+a['name'])}> /Page {page} /OUT pdfmark\n")
        for ridx, row in enumerate(a['layout']['rows'],start=1):
            for cidx, cell in enumerate(row['cells'],start=1):
                for oidx, obj in enumerate(cell['content']['objects'],start=1):
                    url=site+obj['atomic']['file']
                    bn=os.path.basename(unquote(url))
                    filename=f"{aidx:02}-{ridx:02}-{cidx:02}-{oidx:02}-{bn}"
                    #DownloadFile(url, filename)
                    gs.write(f"\n({filename}) viewJPEG showpage \\")
                    page=page+1
            
#        print(f": {len(a['layout']['rows'][0]['cells'])}")
#        pprint(objs, depth=2)

    gs.write("\n\"")
    gs.close()
    pm.close()
    pass

def TOHEX(s):
    return 'feff'+s.encode('utf-16be').hex()

def DownloadFile(url, filename):
    r=requests.get(url,stream=True)
    with open(filename,"wb") as f:
        for data in tqdm(r.iter_content(), desc=bn):
            f.write(data)


