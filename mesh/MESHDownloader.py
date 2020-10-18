#!env python3

import json
from pprint import pprint
from urllib.parse import unquote
from tqdm import tqdm
import os
import requests
import hashlib
from anytree import Node, RenderTree, PreOrderIter
import queue

class MeshArticle():
    """ Класс, представляющий одну статью в материале """
    def __init__(self):
        self.name=""
        self.parent=""
        self.html=""
        pass

""" Download composed_material """
def DownloadCM(js):

    site="https://uchebnik.mos.ru"
    content_name = js['name'] if 'iname' in js  else 'UNKNOWN'
    content_desc = js['description'] if 'description' in js  else 'UNKNOWN'
    content_author = js['user_name'] if 'user_name' in js else 'UNKNOWN'


    print(f"Название: {content_name}")
    print(f"Описание: {content_desc}")

    print(f"Разделов: {len(js['articles'])}")
    page=1

    dlid=1000

    doc=open("output.html", "w")
    doc.write("""
<!DOCTYPE html>
<html>
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
        <title>Играемся</title>
        <link rel="stylesheet" href="mykatex.css" >
 <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.10.0/dist/katex.min.css" integrity="sha384-9eLZqc9ds8eNjO3TmqPeYcDj8n+Qfa4nuSiGYa6DjLNcv9BtN69ZIulL9+8CqC9Y" crossorigin="anonymous">

    <!-- The loading of KaTeX is deferred to speed up page rendering -->
    <script defer src="https://cdn.jsdelivr.net/npm/katex@0.10.0/dist/katex.min.js" integrity="sha384-K3vbOmF2BtaVai+Qk37uypf7VrgBubhQreNQe9aGsz9lB63dIFiQVlJbr92dw2Lx" crossorigin="anonymous"></script>

    <!-- To automatically render math in text elements, include the auto-render extension: -->
    <script defer src="https://cdn.jsdelivr.net/npm/katex@0.10.0/dist/contrib/auto-render.min.js" integrity="sha384-kmZOZB5ObwgQnS/DuDg6TScgOiWWBiVt0plIRkZCmE6rDZGrEOQeHM5PcHi+nyqe" crossorigin="anonymous"
        onload="renderMathInElement(document.body);"></script>
    <script src="render.js"> </script>
    </head>
    <body>
    """)


    m=hashlib.md5()

    TheDocument={}

    for aidx, a in enumerate(js['articles'], start=1):
        #doc.write(f"<h1>{aidx:02}. {a['name']}</h1>")
        art = MeshArticle()
        art.name=a['name']
        art.parent=a['parentId']
        art.id=a['id']
        TheDocument[art.id]=art

#        pm.write(f"[ /Title <{TOHEX(str(aidx)+'. '+a['name'])}> /Page {page} /OUT pdfmark\n")
        for ridx, row in enumerate(a['layout']['rows'],start=1):
            for cidx, cell in enumerate(row['cells'],start=1):
                for oidx, obj in enumerate(cell['content']['objects'],start=1):
                    atomic_type=obj['atomic']['content_type']

                    if atomic_type == 'file':
                        url=site+obj['atomic']['file']
                        bn=os.path.basename(unquote(url))
                        filename=f"download/{aidx:02}-{ridx:02}-{cidx:02}-{oidx:02}-{bn}"
                        DownloadFile(url, filename, "file")
                        #gs.write(f"\n({filename}) viewJPEG showpage \\")
                        page=page+1
                    elif atomic_type == 'text':
                        if 'displayContent' in obj['atomic']:
                            art.html+=obj['atomic']['displayContent']
                    elif atomic_type == 'image':
                        url=site+obj['atomic']['file']
                        ts=url.rfind('?')
                        #print(f"ts: {ts}")
                        extp=url.rfind(".")
                        ext=url[1:ts][extp:]
                        bn=hashlib.md5(url[1:ts].encode('utf-8')).hexdigest()
                        filename=f"download/{bn}.{ext}"
                        DownloadFile(url, filename,
                                os.path.basename(unquote(url[1:ts])))
                        dlid+=1
                        w=obj['block']['width']
                        h=obj['block']['height']
                        art.html+=f"<img src='{filename}' width='{w}' height='{h}'/>"
                    else:
                        print(f"UNKNOWN CONTENT TYPE: {atomic_type}")


            
#        print(f": {len(a['layout']['rows'][0]['cells'])}")
#        pprint(objs, depth=2)

    # формируем структуру документа
    nodes=dict(TheDocument)
    

    print("формируем структуру документа")
    while nodes:
        r=False
        cn=dict(nodes)
        for key,val in cn.items():
            if val.parent in TheDocument:
                nodes.pop(key)
                r=True
      #          print(f"Удалили {key}")
        if not r : 
     #       print("За этот заход так ничего и не удалили")
            break
        else:
    #        print("Удалили, ещё зайдём")
            pass

    topart=list(nodes.values())[0]

    print(f"Остался только один: {topart.name}")

    nodes=dict(TheDocument)
    nodes.pop(topart.id)
    top = Node(topart.id, article=topart, nestlevel=0)

    # Очередь на поиск
    artq=queue.Queue()
    artq.put(top)

    while not artq.empty():
        print(f"Длина очереди: {artq.qsize()}")
        a=artq.get(False)
        for key,value in TheDocument.items():
            if value.parent==a.article.id:
                n = Node(value.id, article=value, parent=a,
                        nestlevel=a.nestlevel+1)
                print(f"Добавили {value.name} в {a.article.name}")
                artq.put(n)

    for pre,fill,node in RenderTree(top):
        print(f"{pre} {node.article.name}")

    for a in PreOrderIter(top):
        doc.write(f"<h{a.nestlevel}>{a.article.name}</h{a.nestlevel}>")
        doc.write(a.article.html)







    


    doc.write("</body></html>")
    doc.close()
    pass

def TOHEX(s):
    return 'feff'+s.encode('utf-16be').hex()

def DownloadFile(url, filename, desc):
    if os.path.isfile(filename):
        print(f"{desc} уже загружен")
        return
#    print(f"Скачиваем {url} в {filename} [ {desc} ]")
#    return
    r=requests.get(url,stream=True)
    with open(filename,"wb") as f:
        for data in tqdm(r.iter_content(), desc=desc, unit="byte", unit_scale=1):
            f.write(data)


