#!env pyton3

import requests
import pdb

from myutils import my_get_post
import os.path

from pprint import pprint


class PGUAuthenticator:
    """ PGU Authenticator """
    def __init__(self, cfg):
        self._ps = requests.Session()
        self._ps.proxies = cfg.proxies
        self._cfg = cfg
        self._ps.headers['User-Agent'] = self._cfg.UA
        self.token = ""
        self.mostoken = ""
        self.Authenticated = False
                
        pass
    

    def Authenticate(self):
        return self.ForceAuthenticate()

        if os.path.isfile("cookies/mos_oauth20_token"):
            with open("cookies/mos_oauth20_token", "r") as t:
                self.mostoken=t.read()

        if os.path.isfile("cookies/Ltpatoken2"):
            with open("cookies/Ltpatoken2","r") as t:
                self.token=t.read()

        if self.token == "" or self.mostoken=="":
            print("Не удалось загрузить прошлые токены, аутентифицируемся заново")
            return self.ForceAuthenticate()
        else:
            print("Пытаемся использовать имеющиеся токены")
            self._ps.cookies['Ltpatoken2'] = self.token
            self._ps.cookies['mos_oauth20_token'] = self.mostoken
            return True
        pass


    def ForceAuthenticate(self):
        try:
            ps=self._ps
            r=my_get_post(ps.get,"https://www.mos.ru")
            #print(r)
            #print("cookies:")
            #print_dict(r.cookies)
            ps.cookies.update(r.cookies)
            r=my_get_post(ps.get,"https://www.mos.ru/api/oauth20/v1/frontend/json/ru/process/enter")
            ps.cookies.update(r.cookies)
            r=my_get_post(ps.get,r.headers['Location'])
            ps.cookies.update(r.cookies)
            r=my_get_post(ps.get,r.headers['Location'])
            ps.cookies.update(r.cookies)
            r=my_get_post(ps.get,r.headers['Location'])

            login_data={ 
                    'j_username' : self._cfg.login, 
                    'j_password' : self._cfg.password, 
                    'accessType' : 'alias'}
            
            r= my_get_post(ps.post,"https://oauth20.mos.ru/sps/j_security_check", data=login_data)

            self.token = self._ps.cookies['Ltpatoken2']

            self._ps.cookies.update(r.cookies)
            r = my_get_post(self._ps.get,r.headers['Location']) # wsauth
            self._ps.cookies.update(r.cookies)
            r = my_get_post(self._ps.get,r.headers['Location']) # result?code=XXX
            self.mostoken = self._ps.cookies['mos_oauth20_token']

            with open("cookies/sudirtokenexp","w") as t:
                t.write(self._ps.cookies['sudirtokenexp'])
            with open("cookies/JSESSIONID", "w") as t:
                t.write(self._ps.cookies['JSESSIONID'])
            with open("cookies/OAUTH20-PHPSESSID", "w") as t:
                t.write(self._ps.cookies['OAUTH20-PHPSESSID'])
            with open("cookies/mos_oauth20_token", "w") as t:
                t.write(self.mostoken)
            with open("cookies/Ltpatoken2", "w") as t:
                t.write(self.token)

#            print_dict(self._ps.cookies)
#            pdb.set_trace()


            #print("mostoken : " ,self.mostoken)

            self.Authenticated = self.mostoken != ""
            #print("Authenticated:", self.Authenticated)
        except:
            self.Authenticated = False

        return self.Authenticated

        
