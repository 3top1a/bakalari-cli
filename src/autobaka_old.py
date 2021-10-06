from datetime import date
import random
import colorama
import requests
from tabulate import tabulate
import os

# https://x.bakalari.cz
url = os.environ['URL']


# Gets the accesstoken. Returns access token
def get_token(username, password):
    _url = url + "/api/login"
    header = {'Content-Type': 'application/x-www-form-urlencoded'}
    params = {'grant_type': 'password', 'client_id': 'ANDR',
              'username': username, 'password': password}

    r = requests.post(url=_url, headers=header, data=params)
    data = r.json()
    access_token = data.get('access_token')
    return access_token

# Gets all needed timetable information. Returns timetable list, subject name dictionary, period starts and ends
def get_timetable(token, date):
    _url = url + "/api/3/timetable/actual"
    header = {'Content-Type': 'application/x-www-form-urlencoded',
              'Authorization': 'Bearer ' + token}
    params = {'date': date}

    # Request it
    r = requests.get(url=_url, headers=header, data=params)
    data = r.json()

    # Make a nice dictionary of Ids : Abbreviations
    subject_names_raw = data.get('Subjects')
    subject_names = {}
    for x in subject_names_raw:
        subject_names[x['Id']] = x['Abbrev']
        if x['Abbrev'] == None:
            subject_names[x['Id']] = x['']

    # Make a nice list of [DayOfWeek, HourID, SubjectId, TeacherId, Theme]
    day_table_raw = data.get('Days')
    day_table = []
    for x in day_table_raw:
        for y in x['Atoms']:
            day_table.append( [ x['DayOfWeek'], y['HourId'], y['SubjectId'], y['TeacherId'], y['Theme'] ] )
    
    #Make a nice list of period starts and ends. { Id : [ Caption, BeginTime, EndTime] }
    hours_raw = data.get('Hours')
    hours = {}
    for x in hours_raw:
        hours[x['Id']] = [x['Caption'], x['BeginTime'], x['EndTime']]

    return day_table, subject_names, hours

#Returns a colored output based on class name
def class_to_colorama(_class):
    rand = random.Random()
    rand.seed(_class)
    fore = rand.randrange(12)
    color = ""
    if fore == 0:
        color += (colorama.Fore.RED)
    elif fore == 1:
        color += (colorama.Fore.GREEN)
    elif fore == 2:
        color += (colorama.Fore.YELLOW)
    elif fore == 3:
        color += (colorama.Fore.BLUE)
    elif fore == 4:
        color += (colorama.Fore.MAGENTA)
    elif fore == 5:
        color += (colorama.Fore.CYAN)
    elif fore == 6:
        color += (colorama.Fore.LIGHTRED_EX)
    elif fore == 7:
        color += (colorama.Fore.LIGHTGREEN_EX)
    elif fore == 8:
        color += (colorama.Fore.LIGHTYELLOW_EX)
    elif fore == 9:
        color += (colorama.Fore.LIGHTBLACK_EX)
    elif fore == 10:
        color += (colorama.Fore.LIGHTMAGENTA_EX)
    elif fore == 11:
        color += (colorama.Fore.LIGHTCYAN_EX)
    
    back = rand.randrange(3)
    if back == 0:
        color += (colorama.Style.DIM)
    elif back == 1:
        color += (colorama.Style.NORMAL)
    elif back == 2:
        color += (colorama.Style.BRIGHT)
    
    return color


#Prints the timetable into a readable table using tabulate. Needs output from get_timetable.
def print_timetable(timetable_info):
    table_raw = timetable_info[0] 
    subjects = timetable_info[1]
    hours = timetable_info[2]
    table = [[]]
    headers = []
    for x in hours:
        headers.append(hours[x][1])
    prev = 1
    day = 0
    for x in table_raw:
        if(day != x[0] - 1):
            day += 1
            table.append([])
            prev = 1
        diff = x[1] - prev - 1
        prev = x[1] 
        for y in range(diff):
            table[day].append(None)
        color = str(class_to_colorama(subjects.get(x[2])))
        name = '' if subjects.get(x[2]) == None else subjects.get(x[2])
        table[day].append(color + name + colorama.Style.RESET_ALL)

    print(tabulate(table, headers = headers, tablefmt="simple"))
    

todays_date = date.today()
print_timetable(get_timetable(get_token(os.environ['PASSWORD'] , os.environ['PASSWORD']), str(todays_date.year) + '-' + str(todays_date.month) + '-' + str(todays_date.day)))
