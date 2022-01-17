import datetime
import random
import colorama
import requests
from tabulate import tabulate
import os
import sys
import getopt
import sympy

# Non-bakalari functions

# function to convert to subscript
def get_sup(x):
    superscript_map = {
        "0": "⁰", "1": "¹", "2": "²", "3": "³", "4": "⁴", "5": "⁵", "6": "⁶",
        "7": "⁷", "8": "⁸", "9": "⁹", "a": "ᵃ", "b": "ᵇ", "c": "ᶜ", "d": "ᵈ",
        "e": "ᵉ", "f": "ᶠ", "g": "ᵍ", "h": "ʰ", "i": "ᶦ", "j": "ʲ", "k": "ᵏ",
        "l": "ˡ", "m": "ᵐ", "n": "ⁿ", "o": "ᵒ", "p": "ᵖ", "q": "۹", "r": "ʳ",
        "s": "ˢ", "t": "ᵗ", "u": "ᵘ", "v": "ᵛ", "w": "ʷ", "x": "ˣ", "y": "ʸ",
        "z": "ᶻ", "A": "ᴬ", "B": "ᴮ", "C": "ᶜ", "D": "ᴰ", "E": "ᴱ", "F": "ᶠ",
        "G": "ᴳ", "H": "ᴴ", "I": "ᴵ", "J": "ᴶ", "K": "ᴷ", "L": "ᴸ", "M": "ᴹ",
        "N": "ᴺ", "O": "ᴼ", "P": "ᴾ", "Q": "Q", "R": "ᴿ", "S": "ˢ", "T": "ᵀ",
        "U": "ᵁ", "V": "ⱽ", "W": "ᵂ", "X": "ˣ", "Y": "ʸ", "Z": "ᶻ", "+": "⁺",
        "-": "⁻", "=": "⁼", "(": "⁽", ")": "⁾"}
    res = str.maketrans(
        ''.join(superscript_map.keys()),
        ''.join(superscript_map.values()))
    return x.translate(res)

def get_sub(x):
    subscript_map = {
        "0": "₀", "1": "₁", "2": "₂", "3": "₃", "4": "₄", "5": "₅", "6": "₆",
        "7": "₇", "8": "₈", "9": "₉", "a": "ₐ", "b": "♭", "c": "꜀", "d": "ᑯ",
        "e": "ₑ", "f": "բ", "g": "₉", "h": "ₕ", "i": "ᵢ", "j": "ⱼ", "k": "ₖ",
        "l": "ₗ", "m": "ₘ", "n": "ₙ", "o": "ₒ", "p": "ₚ", "q": "૧", "r": "ᵣ",
        "s": "ₛ", "t": "ₜ", "u": "ᵤ", "v": "ᵥ", "w": "w", "x": "ₓ", "y": "ᵧ",
        "z": "₂", "A": "ₐ", "B": "₈", "C": "C", "D": "D", "E": "ₑ", "F": "բ",
        "G": "G", "H": "ₕ", "I": "ᵢ", "J": "ⱼ", "K": "ₖ", "L": "ₗ", "M": "ₘ",
        "N": "ₙ", "O": "ₒ", "P": "ₚ", "Q": "Q", "R": "ᵣ", "S": "ₛ", "T": "ₜ",
        "U": "ᵤ", "V": "ᵥ", "W": "w", "X": "ₓ", "Y": "ᵧ", "Z": "Z", "+": "₊",
        "-": "₋", "=": "₌", "(": "₍", ")": "₎"}
    res = str.maketrans(
        ''.join(subscript_map.keys()),
        ''.join(subscript_map.values()))
    return x.translate(res)

# Gets the accesstoken. Returns access token
def get_token(server, password, username):
    _url = server + "/api/login"
    header = {'Content-Type': 'application/x-www-form-urlencoded'}
    params = {'grant_type': 'password', 'client_id': 'ANDR',
              'username': username, 'password': password}

    try:
        r = requests.post(url=_url, headers=header, data=params)
    except requests.exceptions.ConnectionError:
        print("Connection error")
        exit()
    data = r.json()
    access_token = data.get('access_token')
    return access_token


def get_timetable_data_week(server, token):
    _url = server + "/api/3/timetable/actual"
    header = {'Content-Type': 'application/x-www-form-urlencoded',
              'Authorization': 'Bearer ' + token}
    params = {'date': datetime.date.today().strftime('%Y-%m-%d')}

    # Request it
    try:
        r = requests.get(url=_url, headers=header, data=params)
    except ConnectionError:
        print("Connection error")
        exit()
    data = r.json()

    # Make a nice dictionary of Ids : [Abbreviations, Id, Name]
    subject_names_raw = data.get('Subjects')
    subject_names = {}
    for x in subject_names_raw:
        subject_names[x['Id']] = [x['Abbrev'], x['Id'], x['Name']]
        if x['Abbrev'] == None:
            subject_names[x['Id']] = x['']

    # Make a nice list of [DayOfWeek, HourID, SubjectId, TeacherId, Theme, HourAt, RoomId]
    day_table_raw = data.get('Days')
    day_table = []
    for x in day_table_raw:
        for y in x['Atoms']:
            day_table.append([x['DayOfWeek'], y['HourId'], y['SubjectId'],
                             y['TeacherId'], y['Theme'], y['RoomId']])

    # Make a nice list of period starts and ends. { Id : [ Caption, BeginTime, EndTime] }
    hours_raw = data.get('Hours')
    hours = {}
    for x in hours_raw:
        hours[x['Id']] = [x['Caption'], x['BeginTime'], x['EndTime']]

    return day_table, subject_names, hours


def get_timetable_data_today(server, token):
    _url = server + "/api/3/timetable/actual"
    header = {'Content-Type': 'application/x-www-form-urlencoded',
              'Authorization': 'Bearer ' + token}
    params = {'date': datetime.date.today().strftime('%Y-%m-%d')}

    # Request it
    try:
        r = requests.get(url=_url, headers=header, data=params)
    except ConnectionError:
        print("Connection error")
        exit()
    data = r.json()

    # Make a nice dictionary of Ids : [Abbreviations, Id, Name]
    subject_names_raw = data.get('Subjects')
    subject_names = {}
    for x in subject_names_raw:
        subject_names[x['Id']] = [x['Abbrev'], x['Id'], x['Name']]
        if x['Abbrev'] == None:
            subject_names[x['Id']] = x['']

    # Make a nice list of [DayOfWeek, HourID, SubjectId, TeacherId, Theme, HourAt, RoomId, ]
    day_table_raw = data.get('Days')
    day_table = []
    for x in day_table_raw:
        # Use DayOfWeek to determine what is today
        if x['DayOfWeek'] == datetime.datetime.today().weekday() + 1:
            for y in x['Atoms']:
                day_table.append([x['DayOfWeek'], y['HourId'], y['SubjectId'],
                                y['TeacherId'], y['Theme'], y['RoomId']])

    # Make a nice list of period starts and ends. { Id : [ Caption, BeginTime, EndTime] }
    hours_raw = data.get('Hours')
    hours = {}
    for x in hours_raw:
        hours[x['Id']] = [x['Caption'], x['BeginTime'], x['EndTime']]

    return day_table, subject_names, hours


def display_timetable_data_table(data):
    # Default table display like in the web version

    table_raw = data[0]
    subjects = data[1]
    hours = data[2]
    table = [[]]
    headers = []

    # Add all the begin times (7:00 - 7:45, 7:50, ...)
    for x in hours:
        headers.append(hours[x][1] + "\n" + hours[x][2])

    for x in table_raw:
        name = '' if subjects.get(x[2]) == None else subjects.get(x[2])[0]
        day = x[0]

        # Add blank entries if day doesn't exist
        if len(table) == day:
            table.insert(day, [])
            for y in range(0, len(headers)):
                table[day].append('  ')
        table[day][x[1]] = name

    table.remove(table[0])  # Since day starts at 1 by default

    # Save the modified data seperately
    mod_headers = []
    mod_table = []

    # Clear any blank columns
    for header in headers:
        headerindex = headers.index(header)
        column = []

        # Since `table` goes [row[hour, hour], row[hour, hour]]
        for day in table:

            # If there is nothing in the column
            x = day[headers.index(header)]
            column.append(x)

        # Add if not empty
        if(column.count('  ') != len(column)):
            mod_headers.append(header)

            for day in table:
                if len(mod_table) == table.index(day):
                    mod_table.append([])
                mod_table[table.index(day)].append(day[headerindex])

    print(tabulate(mod_table, headers=mod_headers, tablefmt="simple"))
    # print(mod_table)


def display_timetable_data_simple(data):
    # Default table display like in the web version

    table_raw = data[0]
    subjects = data[1]
    hours = data[2]
    table = ['']
    headers = []

    # Init
    for x in range(len(hours)):
        table.append('')

    for x in table_raw:
        # Add blank entries if day doesn't exist
        name = '' if subjects.get(x[2]) == None else subjects.get(x[2])[0]
        day = x[0]
        table[x[1]] = name

    r = ' '.join(str(x) for x in table) # Basically JS's Array.join

    r = r.lstrip().rstrip()

    print(r)

def timetable_week(server, password, username):
    token = get_token(server, password, username)
    display_timetable_data_table(get_timetable_data_week(server, token))

def timetable_simple(server, password, username):
    token = get_token(server, password, username)
    display_timetable_data_simple(get_timetable_data_today(server, token))


def main():
    try:
        opts, args = getopt.gnu_getopt(sys.argv[1:], "hs:p:u:t:c", [
                                       "server", "password", "username", "homework", "compact"])
    except getopt.GetoptError:
        print('main.py -s example.bakalari.cz -p password -u username')
        sys.exit(2)
    server = ""
    password = ""
    username = ""
    simple = False

    for opt, arg in opts:
        if opt == '-h':
            print('main.py -s example.bakalari.cz -p password -u username')
            sys.exit()
        elif opt in ("-s", "--server"):
            server = arg
        elif opt in ("-p", "--password"):
            password = arg
        elif opt in ("-u", "--username"):
            username = arg
        elif opt in ("-c", "--compact"):
            simple = True

    if simple:
        timetable_simple(server, password, username)
    else:
        timetable_week(server, password, username)


if __name__ == "__main__":
    main()
