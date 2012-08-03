# coding=utf8

from models import BaseInterface, StockModel
import csv

class Stock(BaseInterface):
    model = StockModel

    def __init__(self):
        self.engine = StockModel.engine
        self.session = StockModel.session

    def _get_iters_from_file(self, file_obj):
        try:
            return csv.reader(file_obj,delimiter='\t')
        except Exception as e:
            return iter([])

    def _invalid_all(self):
        self.session.query(StockModel).update({'is_valid':False})

    def _process(self, stock):
        no = '%06d' % int(stock[0])
        return {
            'no' : no,
            'name' : stock[1].replace(' ',''),
            'price' : float(stock[2]) and float(stock[2]) or float(stock[3]),
            'market' : no.startswith('6') and 'SH' or 'SZ',
            'is_valid' : stock[4]
        }

    def delete_one(self, stock_no, commit=True):
        for stock in self.session.query(StockModel).filter(stock_no):
            self.session.delete(stock)
        self._commit(commit)

    def update_one(self, stock, commit=True):
        #stock_model, query = self.get(stock[0], query=True)
        #if stock_model:
            #temp = self._process(stock)
            #del temp['no']
            #query.update(temp)
        #else:
            #self.add_one(stock, False)
        #self._commit(commit)

        stock_obj = self.get(stock[0])
        if stock_obj:
            temp = self._process(stock)
            self.session.query(StockModel).filter(StockModel.no==temp['no']).update(temp)
        else:
            self.add_one(stock, False)
        self._commit(commit)



    def initial(self, file_name):
        if self.session.query(StockModel).count():
            self.update(file_name)
            return
        with open(file_name, 'r') as f:
            stocks = self._get_iters_from_file(f)
            print('开始初始化股票数据库...')
            for stock in stocks:
                stock.append(True)
                self.add_one(stock, False)
                print(stock[0], '\t', stock[1])
            self.session.commit()
            print('初始化完成!')
            f.close()

    def update(self, file_name):
        with open(file_name, 'r') as f:
            stocks = self._get_iters_from_file(f)
            self._invalid_all()
            print('开始更新股票数据库...')
            for stock in stocks:
                stock.append(True)
                self.update_one(stock, False)
                print(stock[0], '\t', stock[1])
            self.session.commit()
            print('更新完成!')
            f.close()
