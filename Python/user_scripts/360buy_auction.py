# coding=utf8

import kisopener, json, time

class Auction:
    def __init__(self):
        self.opener = kisopener.Opener()

    @property
    def total_pages(self):
        return self._fetch(page=1).get('totalPages')

    def _fetch(self, page):
        return json.loads(self.opener.urlopen('http://auction.360buy.com/json/paimai/list_auction_deals?cateId=670&pageNo=%s' % page).read().decode('utf8'))

    def fetch(self, page):
        return self._fetch(page=page).get('datas', [])

    def fetch_all(self, is_sorted=False):
        datas = []
        pages = self.total_pages
        print('一共%s页' % pages)
        for page in range(1, pages+1):
            datas.extend(self.fetch(page=page))
            print('成功抓取第%s页' % page)
        return sorted(datas, key=lambda x:x.get('startTime')) if is_sorted else datas

    def print_all(self):
        for item in self.fetch_all(is_sorted=True):
            now = int(time.time())
            start_time = int(item.get('startTime')/1000)
            end_time = int(item.get('endTime')/1000)
            if item.get('status')=='ONBID':
                state = '正在拍卖'
                time_info = end_time - now
            else:
                continue
                state = '等待拍卖'
                time_info = start_time - now
            print('%s\t%s\t%s' % (item.get('title'), state, time_info))

if __name__ == '__main__':
    auction = Auction()
    auction.print_all()


