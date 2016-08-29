#!/usr/bin/env python

import bs4
import getpass
import json
import menu
import os
import re
import requests
import urlparse

LOGIN_URI = 'https://gobble.com/login'
MENU_URI = 'https://gobble.com/account/upcoming'
MENUS_REGEX = re.compile(r'MenusCollection\((.+)\);', re.DOTALL)

class Gobble:
    def __init__(self):
        self.opts = {}

    def configure(self, opts):
        self.opts = opts

    def login(self):
        page = requests.get(LOGIN_URI)
        page_soup = bs4.BeautifulSoup(page.text, 'html.parser')
        login_form = page_soup.find('form', id='login')

        login_data = {}
        for form_field in login_form.find_all('input'):
            value = form_field.get('value')
            if value is None:
                if 'email' in form_field['name']:
                    value = self.opts['email']
                elif 'password' in form_field['name']:
                    value = self.opts['password']
            login_data[form_field['name']] = value
        session = requests.post(urlparse.urljoin(LOGIN_URI, login_form['action']), data=login_data)
        self.opts['cookies'] = session.cookies

    def menu(self, date=None):
        page = requests.get(MENU_URI, cookies=self.opts['cookies'])
        page_soup = bs4.BeautifulSoup(page.text, 'html.parser')
        for cdata in page_soup.findAll(text=True):
            menus = MENUS_REGEX.search(cdata)
            if menus is not None:
                menus = menus.group(1)
                while len(menus) > 0:
                    try:
                        weeks = json.loads(menus)
                        for week in weeks:
                            if date is None:
                                return menu.Menu.from_gobble(week)
                    except ValueError as e:
                        if 'Extra data' in e.message:
                            # Toss any trailing arguments to the class/function we used to anchor the regex
                            menus = menus.rsplit(',', 1)[0]
                        else:
                            raise e

if __name__ == '__main__':
    gobble = Gobble()
    email = raw_input('Please enter your Gobble email address: ')
    password = getpass.getpass('Please enter your Gobble password: ')
    gobble.configure({'email': email, 'password': password})
    gobble.login()
    menu = gobble.menu()
    print unicode(menu)
