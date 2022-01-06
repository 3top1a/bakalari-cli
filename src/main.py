from datetime import date
import random
import colorama
import requests
from tabulate import tabulate
import os
import sys
import getopt


# Gets the accesstoken. Returns access token
def get_token(server, password, username):
    _url = server + "/api/login"
    header = {'Content-Type': 'application/x-www-form-urlencoded'}
    params = {'grant_type': 'password', 'client_id': 'ANDR',
              'username': username, 'password': password}

    r = requests.post(url=_url, headers=header, data=params)
    data = r.json()
    access_token = data.get('access_token')
    return access_token


def get_timetable_data(server, token):
    _url = server + "/api/3/timetable/actual"
    header = {'Content-Type': 'application/x-www-form-urlencoded',
              'Authorization': 'Bearer ' + token}
    params = {'date': date}

    # Request it
    r = requests.get(url=_url, headers=header, data=params)
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


def timetable(server, password, username):
    token = get_token(server, password, username)
    display_timetable_data_table(get_timetable_data(server, token))

# Parsing


def main():
    try:
        opts, args = getopt.gnu_getopt(sys.argv[1:], "hs:p:u:t", [
                                       "server", "password", "username", "homework"])
    except getopt.GetoptError:
        print('main.py -s example.bakalari.cz -p password -u username')
        sys.exit(2)
    server = ""
    password = ""
    username = ""

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

    timetable(server, password, username)


if __name__ == "__main__":
    main()
