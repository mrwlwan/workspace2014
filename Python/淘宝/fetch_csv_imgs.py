# coding=utf

import kisurllib
import os, sys, csv, re, itertools

class ImageFetcher:
    def __init__(self, filename):
        self.csv_file = open(filename, encoding='utf16')
        # 去掉首行
        self.csv_file.readline()
        self.reader = csv.DictReader(self.csv_file, delimiter='\t', lineterminator='\n')
        self.titles = next(self.reader)

    def parse_main_image_urls(self, row):
        """ 抓取主图. """
        reg = re.compile(r'https?://[^\'"|;]+')
        return reg.findall(row.get('picture'))

    def parse_desc_image_urls(self, row):
        """ 抓取宝贝描述图. """
        reg = re.compile(r'src=[\'"]+(https?://[^\'"|;]+)')
        return reg.findall(row.get('description'))

    def fetch_image(self, url, saved_path):
        """ 网络抓取图片并保存. """
        img = kisurllib.urlopen(url).read()
        with open(saved_path, 'wb') as f:
            f.write(img)

    def _mkdir(self, path):
        """ 创建文件夹. """
        if not os.path.exists(path) or os.path.isfile(path):
            os.makedirs(path)

    def action(self):
        for row in self.reader:
            outer_id = row.get('outer_id')
            for urls_info in [
                (self.parse_main_image_urls(row), '主图'),
                (self.parse_desc_image_urls(row), '宝贝描述')
            ]:
                index = itertools.count(1)
                for url in urls_info[0]:
                    path = os.path.join(outer_id, urls_info[1])
                    self._mkdir(path)
                    ext_index = url.rindex('.')
                    if ext_index < 0 or ext_index >= len(url)-1:
                        ext = 'jpg'
                    else:
                        ext = url[ext_index+1:]
                    path = os.path.join(path, '%s-%02d.%s' % (outer_id, next(index), ext))
                    self.fetch_image(url, path)
                    print(path)

if __name__ == '__main__':
    print(sys.argv)
    if len(sys.argv)<2:
        sys.exit()
    filename = sys.argv[1]
    fetcher = ImageFetcher(filename)
    fetcher.action()
