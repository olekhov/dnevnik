#!env python3

import calendar
import requests
import time
import random
import json
import re
import pdb

from pprint import pprint

from dateutil.parser import *
import datetime

from utils import my_get_post, print_dict



"""
Class to access to E-Diary
"""

class Dnevnik:
    """ Class to access electronic diary """
    def __init__(self, pgu_auth):
        """ pgu_auth: authenticator class for PGU """
        self._auth=pgu_auth
        self._data_url="https://my.mos.ru/data/"
        self._authenticated=False
        

    def Authenticate(self):
        """ authentication to PGU """
        if not self._auth.Authenticated:
            self._auth.Authenticate()

        self._ps=self._auth._ps
        ps=self._ps
#        pdb.set_trace()
        ps.cookies["mos_id"]="CllGxlmW7RAJKzw/DJfJAgA="

        milisecs=calendar.timegm(time.gmtime())*1000+random.randint(0,999)+1
        r=my_get_post(ps.get, "https://my.mos.ru/static/xdm/index.html?nocache="+str(milisecs)+"&xdm_e=https%3A%2F%2Fwww.mos.ru&xdm_c=default1&xdm_p=1")
        ps.cookies.update(r.cookies)
        r=my_get_post(ps.get,r.headers['Location'])
        ps.cookies.update(r.cookies)
        r=my_get_post(ps.get,r.headers['Location'])
        ps.cookies.update(r.cookies)
        r=my_get_post(ps.get,r.headers['Location'])
        ps.cookies.update(r.cookies)
        
        # system_id: mos.ru
        r=my_get_post(ps.get,"https://www.mos.ru/api/oauth20/v1/frontend/json/ru/options")
        opts=json.loads(r.text)

        # надо: nonce signature timestamp
        #print("token request cookies:")
        #print_dict(ps.cookies)
        token_data={
                "system_id":opts["elk"]["system_id"],
                "nonce":opts["elk"]["nonce"],
                "timestamp":opts["elk"]["timestamp"],
                "signature":opts["elk"]["signature"]}
        ps.cookies["mos_user_segment"]="default"
        r=my_get_post(ps.post,self._data_url+"token", data=token_data)

        self._mos_ru_token=json.loads(r.text)["token"]

        r=my_get_post(ps.get, "https://www.mos.ru/")
        ps.cookies.update(r.cookies)
        ps.cookies["mos_user_segment"]="default"
        r=my_get_post(ps.get,"https://www.mos.ru/pgu/ru/application/dogm/journal/?onsite_from=popular",
                headers={"referer":"https://www.mos.ru/"})
        # expect 301 redirect https://www.mos.ru/pgu/ru/application/dogm/journal/?onsite_from=popular
        ps.cookies.update(r.cookies)        

        # obtain PHPSESSID
        # 302 redirect to https://oauth20.mos.ru/sps/oauth/oauth20/authorize
        r=my_get_post(ps.get,r.headers['Location'])
        ps.cookies.update(r.cookies)
        # 302 redirect to https://www.mos.ru/pgu/ru/oauth/?code=74...       
        r=my_get_post(ps.get,r.headers['Location'])
        ps.cookies.update(r.cookies)
        # 200 redirect to https://www.mos.ru/pgu/ru/services/link/2103/?onsite_from=3532
        r=my_get_post(ps.get,r.headers['Location'])
        ps.cookies.update(r.cookies)

        r=my_get_post(ps.get, "https://www.mos.ru/pgu/ru/application/dogm/journal/")
        
        self.dnevnik_top_referer = r.headers['Location']

        # 200 redirect to https://www.mos.ru/pgu/ru/services/link/2103/?onsite_from=3532
        r=my_get_post(ps.get,r.headers['Location'])

        # Тут мы в https://dnevnik.mos.ru/?token=64749fb9596a7f2078090a894ab31452
        m=re.search('.*token=(.*)', self.dnevnik_top_referer)
        self._auth_token=m.group(1)

        opts = { "auth_token": self._auth_token }
        
        r=my_get_post(ps.post, "https://dnevnik.mos.ru/lms/api/sessions",
                headers={"referer": self.dnevnik_top_referer}, json=opts)

        self._profile=json.loads(r.text)
        self._pid=str(self._profile["profiles"][0]["id"])
        self._ids=str(self._profile["profiles"][0]["user_id"])
        self.Authenticated = self._auth_token != ""
        return self.Authenticated

    def SelectAcademicYear(self, year_id):
        ps=self._ps
        year_id=str(year_id)

        ps.headers["Auth-Token"]=self._auth_token
        ps.cookies["authtype"]="1"
        ps.cookies["aid"]=year_id
        ps.cookies["auth_token"]=self._auth_token
        ps.cookies["is_auth"]="true"
        ps.cookies["profile_id"]=self._pid
        r=my_get_post(ps.get, "https://dnevnik.mos.ru/desktop",
                headers={"referer":self.dnevnik_top_referer})
        
        opts = { "auth_token": self._auth_token }
        r=my_get_post(ps.post,f"https://dnevnik.mos.ru/lms/api/sessions?pid={self._profile['profiles'][0]['id']}",
                json=opts, headers={"referer":"https://dnevnik.mos.ru/desktop"})

        pass

    def ListStudents(self):
        ps=self._ps
        headers={"referer"    : "https://dnevnik.mos.ru/desktop", 
            "Accept"     : "application/json",
            "Profile-Id" : self._pid}        
        
        r=my_get_post(ps.get,f"https://dnevnik.mos.ru/acl/api/users?ids={self._ids}&pid={self._pid}", headers=headers)
        
        j=json.loads(r.text)
        result=[]
        r=my_get_post(ps.get,"https://dnevnik.mos.ru/core/api/student_profiles?pid={self._pid}",
            headers=headers)
        j=json.loads(r.text)
        return j

    def OpenDiary(self, student_id):
        ps=self._ps

        self._sh={"referer" : f"https://dnevnik.mos.ru/manage/student_journal/{student_id}",
                "Accept" : "application/vnd.api.v3+json",
                "Auth-Token" : self._auth_token,
                "Profile-Id" : self._pid}

        r=my_get_post(ps.get,f"https://dnevnik.mos.ru/manage/student_journal/{student_id}")
        r=my_get_post(ps.post,f"https://dnevnik.mos.ru/lms/api/sessions?pid={self._pid}",
            headers=self._sh)
        self._sh["Accept"]="application/json"
        self.LoadGroups(student_id)
        self.LoadSchedule(student_id)
        return

    def LoadGroups(self, student_id):
        ps=self._ps
        params={
                "academic_year_id":"6",
                "pid":self._pid,
                "with_archived_groups":"true",
                "with_groups":"true" }
        r=my_get_post(ps.get,f"https://dnevnik.mos.ru/core/api/student_profiles/{student_id}",
                headers=self._sh, params=params)
        self.groups=json.loads(r.text)['groups']
        pass

    def LoadSchedule(self, student_id):
        ps=self._ps
        gs=[]
        for g in self.groups:
            gs.append(str(g['id']))
        params={ "group_ids" : ','.join(gs),"pid":self._pid}
        r=my_get_post(ps.get,f"https://dnevnik.mos.ru/jersey/api/groups",
                headers=self._sh, params=params)
        self.schedule=json.loads(r.text)

        self.sched_dict={}
        for s in self.schedule:
            self.sched_dict[s['id']]=s
        pass

    def GetHomework(self, year_id, student_id, begin_date, end_date):
        ps=self._ps

        params={
                "academic_year_id":year_id,
                "begin_date":begin_date,
                "end_date": end_date,
                "pid":self._pid,
                "student_profile_id":student_id}

        r=my_get_post(ps.get,f"https://dnevnik.mos.ru/core/api/student_homeworks", headers=self._sh, params=params)

        j=json.loads(r.text)

        for h in j:
            cr=parse(h['homework_entry']['created_at'])
            dt_assigned=parse(h['homework_entry']['homework']['date_assigned_on'])
            if cr>dt_assigned+datetime.timedelta(days=2):
                h['fair']=False
            else:
                h['fair']=True
        return j


        pass

    def GetMarks(self,student_id, created_from, created_to):
        ps=self._ps

        params={
                "created_at_from":created_from,
                "created_at_to"  :created_to,
                "page":"1", "per_page":"50",
                "pid" : self._pid,
                "student_profile_id": student_id}
        r=my_get_post(ps.get,"https://dnevnik.mos.ru/core/api/marks",
                params=params, headers=self._sh)
        j=json.loads(r.text)

        return j



class DiaryProfile:
    """ """
    def __init__(self, login, comment, password, system):
        self.login=login
        self.comment=comment
        self.password=password
        self.system=system

    def __repr__(self):
        return "r[%s] : login=%s password=%s\n" %(self.comment, self.login, self.password)
        
    def __str__(self):
        return "s[%s] : login=%s password=%s\n" %(self.comment, self.login, self.password)



