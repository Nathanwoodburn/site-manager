import os
import json
import hashlib
import getpass
import random
import datetime



def create_account():
    # Save account to file ./accounts.json
    # Create file if it doesn't exist
    if not os.path.isfile('accounts.json'):
        with open('accounts.json', 'w') as file:
            file.write('[]')
    
    # Load accounts
    with open('accounts.json', 'r') as file:
        accounts = json.loads(file.read())

    # Get account data
    username = input('Username: ').lower()
    password = getpass.getpass('Password: ')


    # Check if username already exists
    for account in accounts:
        if account['username'] == username:
            print('Username already exists')
            return
    
    # Hash password
    password = hashlib.sha256(password.encode()).hexdigest()


    # Add account to accounts
    accounts.append({
        'username': username,
        'password': password
    })

    # Save accounts
    with open('accounts.json', 'w') as file:
        file.write(json.dumps(accounts))

    print('Account created')

def login(user,password):
    if not os.path.isfile('accounts.json'):
        return False

    # Load accounts
    with open('accounts.json', 'r') as file:
        accounts = json.loads(file.read())

    # Hash password
    password = hashlib.sha256(password.encode()).hexdigest()

    # Check if username and password match
    for account in accounts:
        if account['username'] == user.lower() and account['password'] == password:
            return True

    return False

def generate_cookie(username):
    # Generate a random cookie
    cookie = hashlib.sha256(str(random.random()).encode()).hexdigest()

    if not os.path.isfile('cookies.json'):
        with open('cookies.json', 'w') as file:
            file.write('[]')

    # Save cookie to file
    with open('cookies.json', 'r') as file:
        cookies = json.loads(file.read())

    time = datetime.datetime.now() + datetime.timedelta(days=30)
    
    cookies.append({
        'username': username,
        'cookie': cookie,
        'expiration': time.timestamp()
    })

    with open('cookies.json', 'w') as file:
        file.write(json.dumps(cookies))

    return cookie

def check_cookie(cookie):
    if not os.path.isfile('cookies.json'):
        return False

    with open('cookies.json', 'r') as file:
        cookies = json.loads(file.read())

    for c in cookies:
        if c['cookie'] == cookie:
            if c['expiration'] > datetime.datetime.now().timestamp():
                return c['username']
            else:
                cookies.remove(c)
                with open('cookies.json', 'w') as file:
                    file.write(json.dumps(cookies))
                return False

    return False
    


if __name__ == '__main__':
    create_account()