#!env python3

import dnevnik
import pdb

from colorama import init, Fore, Back, Style

from pguauth import PGUAuthenticator
from dnevnik import Dnevnik
from libmesh import MESHLibrary

from gosuslugi_config import cfg

from pprint import pprint
import json

init()
print(f"Вход на {Style.BRIGHT}{Fore.WHITE}ГОС{Fore.BLUE}УСЛ{Fore.RED}УГИ{Style.RESET_ALL}: ",
        end="")
auth = PGUAuthenticator(cfg)

# pdb.set_trace()
if auth.Authenticate() :
    print(f"{Style.BRIGHT}{Fore.GREEN}OK{Style.RESET_ALL}")
else:
    print(f"{Style.BRIGHT}{Back.RED}Ошибка!{Style.RESET_ALL}")
    exit()


#print("GOSUSLUGI TOKEN:")
#print(auth.token)
#print(auth.mostoken)
print(f"Вход в электронный дневник: ", end="")
d = Dnevnik(auth)
if d.Authenticate():
    print(f"{Style.BRIGHT}{Fore.GREEN}OK{Style.RESET_ALL}")
else:
    print(f"{Style.BRIGHT}{Back.RED}Ошибка!{Style.RESET_ALL}")
    exit()
print(d._profile)
print("Вход осуществлён пользователем: %s %s %s" % (
    d._profile['first_name'],
    d._profile['middle_name'],
    d._profile['last_name']))
print("Роль: ", "Родитель" if d._profile['profiles'][0]['type'] == 'parent' else "Ученик")

students = d.ListStudents()
for i,s in enumerate(students, start=1):
    print(f"{i}. {s['user_name']}")

kid=2
d.OpenDiary(students[kid]['id'])
marks= d.GetMarks(students[kid]['id'],"17.09.2018","24.09.2018")

for m in marks:
    print(f"{d.sched_dict[m['group_id']]['subject_name']}: {m['name']}")


hw = d.GetHomework(students[kid]['id'],"24.09.2018","30.09.2018")

for h in hw:
    print(f"{Fore.BLUE}{d.sched_dict[h['homework_entry']['homework']['group_id']]['subject_name']}{Style.RESET_ALL}  ",
            end="")
    if not h['fair']:
        print(f"{Back.RED}",end="")
    print(f"{h['homework_entry']['created_at']} : "
        f"{h['homework_entry']['homework']['date_assigned_on']} -- "
        f"{h['homework_entry']['homework']['date_prepared_for']}{Style.RESET_ALL}")
    print(h['homework_entry']['description'])


#pprint(hw)

#pprint(students)
#j = d.ListProfiles()
#print(j[3])
#d.SelectProfile(j[3])


