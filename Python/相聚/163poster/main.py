#!/usr/bin/python3
# coding=utf8

from poster163 import Poster163
import mylib

if __name__ == '__main__':
    configs = mylib.get_configs('config.cfg', encoding='utf8')
    section_keys = [key for key in configs if key.lower().startswith('section')]
    posters = []
    for section_key in section_keys:
        for auth in configs[section_key].pop('auths').split(','):
            username, password = auth.split(':')
            auth = {'username': username.strip(), 'password': password.strip()}
            poster = Poster163(auth, configs['global'], configs[section_key])
            posters.append(poster)
    print('\n开始灌水...\n')
    for poster in posters:
        poster.start()
    for poster in posters:
        poster.join()
