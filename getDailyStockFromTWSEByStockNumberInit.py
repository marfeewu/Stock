#-*- coding: utf-8 -*-
#standoard package and module load
import sys,os
import traceback
from package.stock import configload
from package.stock import stocklog
from package.stock import dbaction
from package.stock import stockparser
from datetime import datetime,date
import time
from dateutil.relativedelta import relativedelta

#config load
cfg = configload.loadcfg()

#log initial
plog = stocklog.processloginitial(cfg)




def main():
    plog.info("----------日誌記錄開始:抓取上市股票股價----------")
    data = []
    global error_code
    error_code = 0
    stockidlist_tmp = []
    stockidlist = dbaction.qGetAllStockByCategoryType(1)
#排除已成功抓取股價資料的股票代碼
    logpath = cfg['path']['logPath']
    updatelogfolder = './' + logpath + '/' + 'update/'
    now = date.today()
    filfullename = updatelogfolder + str(now.year) + str(now.month).zfill(2) + '.csv'
    if os.path.exists(filfullename):
        excludelist = []
        csvfile = open(filfullename, 'r')
        for row in csvfile:
            excludelist = row.strip('\n').split(sep=',')
        stockidlist_tmp[:] = [x for x in stockidlist if x not in excludelist]
        stockidlist = stockidlist_tmp

    from_date = datetime.today().replace(day=1)
    to_date = from_date + relativedelta(years=0-int(cfg['quotedatarange']['duration']))
    try:
        for x in stockidlist :
            print ("stockidlist", x, "from_date", from_date, "to_date", to_date)
            data.append(stockparser.getStockCSVDataByStockNo(x,from_date,to_date))
    except :
        error_code = 1
#寫入部份已完整讀取之股價資料
        for i in data :
            for x in i :
                dbaction.insertSimpleDailyQuotes(x)

        plog.error(sys.exc_info())
        plog.error(traceback.print_exc())
        pass
    if error_code == 0 :
        for i in data :
            for x in i :
                dbaction.insertSimpleDailyQuotes(x)
    plog.info("----------日誌記錄結束:抓取上市股票股價----------")

if __name__ == '__main__':
    main()
    while error_code == 1:
        time.sleep(2)
        main()




