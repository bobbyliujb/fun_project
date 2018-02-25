#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests, sys

def login(url, username, password):
    client = requests.session()

    # Retrieve the CSRF token first
    client.get(url)  # sets cookie
    if 'csrftoken' in client.cookies:
        csrftoken = client.cookies['csrftoken']
    else:
        csrftoken = client.cookies['csrf']

    print(username + ' ' + password + ' ' + csrftoken)
    login_data = dict(username=username, password=password, csrfmiddlewaretoken=csrftoken, next='/')
    r = client.post(url, data=login_data, headers=dict(Referer=url))
    with open('lc.html', 'w') as f:  # Use file to refer to the file object
        f.write(r.text)
    return r

def main():
    print(len(sys.argv))
    if len(sys.argv) < 3:
        print('Usage: python3 auto_login.py <username> <password>')
        return
    url = 'https://leetcode.com/accounts/login/'
    username = sys.argv[1]
    password = sys.argv[2]
    print(login(url, username, password).status_code)

if __name__ == "__main__":
    main()