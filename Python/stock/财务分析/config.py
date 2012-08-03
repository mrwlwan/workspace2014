# coding=utf8

WEB_CHARSET = 'GBK'
CORP_URL = 'http://vip.stock.finance.sina.com.cn/corp/go.php'
# 公司简介抓取页面
CORP_INFO_URL = CORP_URL + '/vCI_CorpInfo/stockid/%06s.phtml'
# 股本结构抓取页面
STOCK_STRUCTURE_URL = CORP_URL + '/vCI_StockStructure/stockid/%06s.phtml'
# 流通股东抓取页面
CIRCULATE_STOCK_HOLDER_URL = CORP_URL + '/vCI_CirculateStockHolder/stockid/%06s/displaytype/30.phtml'

