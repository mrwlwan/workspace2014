# coding=utf8

from poster import Poster
import mylib, re


if __name__ == '__main__':
    configs = mylib.get_configs('config.cfg', encoding='utf8')

    posters = []
    for section in configs:
        if not section.startswith('section'):
            continue
        for user in configs[section]['auths'].split(','):
            print(user)
            configs[section].update({'auth':user})
            posters.append(Poster('config.cfg', configs[section]))
            print('ok')
    print('ok')
    for poster in posters:
        poster.start()
    for poster in posters:
        poster.join()
