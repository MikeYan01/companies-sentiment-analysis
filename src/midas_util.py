# -*- coding: utf-8 -*-
"""
Created on 7/18/2018

@author: Andy
"""

import sys
import os, json
#!/usr/bin/env python
import psycopg2
import rarfile
import re
import numpy as np
import pandas as pd
import pandas.io.sql as sqlio
import math
import pickle
from sqlalchemy import create_engine
import tushare as ts

debug_mode = False

if sys.version_info[0] < 3:
    import codecs

    _open_func_bak = open  # Make a back up, just in case
    open = codecs.open

class MockXTransformer(object):
    """
    Mock transformer that accepts no y argument.
    """
    def fit(self, X):
        return self

    def transform(self, X):
        return X


class MockTClassifier(object):
    """
    Mock transformer/classifier.
    """
    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return X

    def predict(self, X):
        return True

# reshape data into (-1,1)
def v_reshape(x):
    try:
        if (x > 0):
            return 1/math.exp(x)
        else:
            return -1/math.exp(x)
    except:
        return 0.0

def log_reshape(x):
    try:
        if (x < 1 ):
            return math.exp(x) - 1
        elif (x > 10000):
            return 1
        else:
            return math.log(x)/10
    except:
        return 0.0

def toFloat(x):
    try:
        return np.float(x)
    except:
        return 0.0

def toRatings(x):
    val = 0.0
    if (x == "NULL"):
        val = -1
    elif (x == "STRONG SELL"):
        val = 1
    elif (x in ["SELL","UNDER PERFORM","UNDER WEIGHT"]):
        val = 2
    elif (x in ["MARKET PERFORM","HOLD","EQUAL WEIGHT"]):
        val = 3
    elif (x in ["BUY","OUTER PERFORM","OVER WEIGHT"]):
        val = 4
    elif (x in ["STRONG BUY"]):
        val = 5
    else:
        val = x
    return v_reshape(val)

class RatingEncoder():
    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return X.apply(toRatings)

    def fit_transform(self,X,y=None):
        return self.fit(X,y).transform(X)
        
class DateEncoder():
    def fit(self, X, y=None):
        return self

    def transform(self, X):
        dt = X.dt
        return pd.concat([dt.year, dt.month, dt.day], axis=1)

        
def get_pickling_errors(obj,seen=None):
    if seen == None:
        seen = []
    try:
        state = obj.__getstate__()
    except AttributeError:
        return
    if state == None:
        return
    if isinstance(state,tuple):
        if not isinstance(state[0],dict):
            state=state[1]
        else:
            state=state[0].update(state[1])
    result = {}    
    for i in state:
        try:
            pickle.dumps(state[i],protocol=2)
        except pickle.PicklingError:
            if not state[i] in seen:
                seen.append(state[i])
                result[i]=get_pickling_errors(state[i],seen)
    return result
    
class Util:
    
    @staticmethod
    def pickup_num(self, source_string):
        strlist = re.findall(r'\d+\.?\d*', source_string)
        if len(strlist) > 0:
            return strlist[0]
        else:
            return source_string

    def unrar(self, dpath, xpath, passwd):
        for rar in os.listdir(dpath):
            filepath = os.path.join(dpath, rar)
            with rarfile.RarFile(filepath) as opened_rar:
                for f in opened_rar.infolist():
                    print (f.filename, f.file_size)
                opened_rar.extractall(xpath,pwd=passwd)

    def json2table(self, jsondata, server, usr, pwd, dbname, tablename, companyid):
        conn = psycopg2.connect(database=dbname, user=usr, 
            password=pwd, host=server, port='5432')
        cur = conn.cursor()
        for item in jsondata:
            fields = "insert into media ("
            values = " VALUES("
            for key,value in item.items():
                values += "'"+value.replace("'", "^")+"',"
                fields += key + ","
            #adding companyid
            fields += "company_id)"
            values += "'"+companyid+"')"
            # need a placeholder (%s) for each variable 
            # refer to postgres docs on INSERT statement on how to specify order
            # print (fields,values.encode("utf-8"))
            cur.execute(fields+values)
        # commit changes
        conn.commit()
        # Close the connection
        conn.close()    

    def qry2df(self, server, usr, pwd, dbname, qry):
        conn = psycopg2.connect(database=dbname, user=usr, 
            password=pwd, host=server, port='5432')
        df = sqlio.read_sql_query(qry, conn)
        #cur = conn.cursor()
        #cur.execute(qry)
        #df = pd.DataFrame(cur.fetchall(), columns)
        # commit changes
        conn.commit()
        # Close the connection
        conn.close()
        return df

        
    def pkl2table(self, pklfile,server, usr, pwd, dbname, tablename):
        engine = create_engine('postgresql://'+usr+':'+pwd+'@'+server+':5432/'+dbname)        
        df = pd.read_pickle(pklfile)
        df.to_sql(tablename, engine)

    def stock2table(self, stock,server, usr, pwd, dbname):
        engine = create_engine('postgresql://'+usr+':'+pwd+'@'+server+':5432/'+dbname)        
        df = ts.get_hist_data(stock)
        df.to_sql('ts_'+stock.strip(), engine)

if __name__ == '__main__':

    util = Util()
    #file
    print('program start')

    if len(sys.argv) < 3:
        print('input parameters: midas_util function param1 param2 param3 param4')
        print('		j2table - Json file directory to table')
        print('		rarextract - Extract rarfiles into folder')
        print('		pkl2table - pickle file to postgresql table')
    elif sys.argv[1] == 'j2table':
        print ('Json dir:',sys.argv[2],' Server:',sys.argv[3], ' Database:', sys.argv[4], ' Table:', sys.argv[5], ' user pwd')
        file_dir = sys.argv[2]
        files = [pos_json for pos_json in os.listdir(file_dir) if pos_json.endswith('.json')]

        # we need both the json and an index number so use enumerate()
        for index, js in enumerate(files):
            with open(os.path.join(file_dir, js), encoding="utf8") as json_file:
                json_text = json.load(json_file)
                util.json2table(json_text,sys.argv[3], sys.argv[6],sys.argv[7],sys.argv[4],sys.argv[5], sys.argv[8])

    elif sys.argv[1] == 'pkl2table':
        print ('pickle file:',sys.argv[2],' Server:',sys.argv[3], ' Database:', sys.argv[4], ' Table:', sys.argv[5], ' user pwd')
        file_name = sys.argv[2]
        util.pkl2table(file_name,sys.argv[3], sys.argv[6],sys.argv[7],sys.argv[4],sys.argv[5])

    elif sys.argv[1] == 'stock2table':
        print ('stock:',sys.argv[2],' Server:',sys.argv[3], ' Database:', sys.argv[4], ' Table:tu_', sys.argv[2], ' user pwd')
        company_id = sys.argv[2]
        util.stock2table(company_id,sys.argv[3], sys.argv[5],sys.argv[6],sys.argv[4])
        
    print('program end ')
