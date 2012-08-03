from mylib import Opener, get_configs
import re, time

class Register_batcher():
    def __init__(self, config_path='config.cfg'):
        self.opener = Opener()
        self._sections= get_configs(config_path)
        self.global_config = self._sections['global']
        self.user_config = self._sections['user_section']

    def process_user_section(self):
        names = []
        usernames = self.user_config['usernames']
        reg = re.compile(r'(?P<name>[^ ]+?)\[(?P<start>\d+?)-(?P<end>\d+?)\]@(?P<mail_prefix>[^ ]+)')
        for name in reg.finditer(usernames):
            names.append(name.groupdict())
        password = self.user_config['password']
        mails = [mail.strip() for mail in re.split(r' +|\t+', self.user_config['mails'])]
        return {
            'names': names,
            'password': password,
            'mails': mails
        }

    def update_formhash(self):
        url = self.global_config['reg_url']
        html = self.opener.open(url).decode(self.global_config['charset'], errors='ignore')
        search_obj = re.search(r'formhash" value="(?P<formhash>[^"]*)', html)
        search_obj and self.global_config.update({'formhash': search_obj.groups()[0]})

    def register(self, user, f):
        url = self.global_config['reg_url']
        name = user['name']
        post_data = {
            'username': user['name'],
            'password': user['password'],
            'password2': user['password'],
            'refer': 'space.php?do=home',
            'formhash': self.global_config['formhash'],
            'registersubmit': '注册新用户'
        }
        for mail in user['mails']:
            post_data['email'] = '%s@%s' % (user['mail_prefix'], mail)
            response_content = self.opener.open(url, data=post_data)
            if response_content.find('注册成功'.encode('gbk')) >= 0:
                print('%s 注册成功' % user['name'])
                f.write('%s\t%s\t%s\n' % (user['name'], user['password'], post_data['email']))
                break
            elif response_content.find('已经存在'.encode('gbk')) >= 0:
                print('%s 用户名或者邮箱已经注册过' % user['name'])
                break
        else:
            print('%s %s' % (user['name'], '注册失败'))

    def action(self):
        self.update_formhash()
        print(self.global_config['formhash'])
        f = open('成功注册用户文件.txt', 'w')
        f.write('用户名\t密码\t邮箱\n')
        f.close()
        f = open('成功注册用户文件.txt', 'a')
        user_section = self.process_user_section()
        print('分析配置文件结果:')
        print(user_section)
        print('****************************************')
        for user in user_section['names']:
            name = user['name']
            start = user['start']
            end = user['end']
            max_len = max(len(start), len(end))
            for i in range(int(start), int(end)+1):
                subfix = '{0:0{1}d}'.format(i, max_len)
                self.register({'name': name + subfix, 'mail_prefix': user['mail_prefix']+subfix, 'password': user_section['password'], 'mails': user_section['mails']}, f)
                if int(self.global_config['delay']):
                    time.sleep(int(self.global_config['delay']))
        print('Done')


if __name__ == '__main__':
    batcher = Register_batcher()
    batcher.action()
    input('\n按任意键结束...')
