#!env python3
# -*- coding: utf-8 -*- 

import requests


def my_get_post(f,url, **kwargs):
    """ Try to GET or POST up to maxtries times. 
    If it fails - raise the exception.

    Used to counter bogus pgu.mos.ru responses. 
    Some times it does not work for the first (and second) connection. """
    maxtries=5
    attempt=0
    havedata=False
    #print("request:",url)
    while attempt<maxtries:
        try:
            r=f(url,allow_redirects=False, **kwargs)
            return r
        except Exception as e:
            print(e)
            attempt+=1
    raise "Can not connect"

def print_dict(d):
    """ Pretty dictionary printer. For debugging """
    for key, value in d.items() :
            print ("["+key+"]=["+str(value)+"]")

