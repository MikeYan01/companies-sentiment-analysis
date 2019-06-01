from __future__ import division  
import sys
import numpy as np
import pandas as pd
import midas_util as md
import time
import datetime
from sklearn import cluster as cl # datasets
from sklearn.model_selection import train_test_split
from keras.models import Sequential
from keras.layers import Dense
from sklearn import metrics
from keras.models import load_model

input_column=['total_cnt', 'view_cnt', 'comment_cnt','positive_cnt','negative_cnt', 'news_cnt','mblog_cnt',
              'blog_cnt','twitter_cnt', 'qq_cnt', 'weichat_cnt','video_cnt', 'finance_cnt', 'govt_cnt', 'company_cnt', 'headline_cnt', 'cluster']

num_clusters = 10
qry_text = "select company_id, substring(publish_time,1,4) || substring(publish_time,5,2) as report_key, \
	count(*) as total_cnt, \
	sum(cast(coalesce(cnt_review,'0') as int)) as view_cnt, \
	sum(cast(coalesce(cnt_comment,'0') as int)) as comment_cnt, \
	sum(case when cast(coalesce(extend1,'0') as int) > 0 then 1 else 0 end) as positive_cnt, \
	sum(case when cast(coalesce(extend1,'0') as int) < 0 then 1 else 0 end) as negative_cnt, \
	sum(case when cont_source in ('10', '11') then 1 else 0 end) as news_cnt, \
	sum(case when cont_source in ('30') then 1 else 0 end) as mblog_cnt, \
	sum(case when cont_source in ('50') then 1 else 0 end) as blog_cnt, \
	sum(case when cont_source in ('31') then 1 else 0 end) as twitter_cnt, \
	sum(case when cont_source in ('40') then 1 else 0 end) as qq_cnt, \
	sum(case when cont_source in ('51') then 1 else 0 end) as weichat_cnt, \
	sum(case when cont_source in ('60') then 1 else 0 end) as video_cnt, \
	sum(case when site_type in ('股票','财经') then 1 else 0 end) as finance_cnt, \
	sum(case when site_type in ('政府') then 1 else 0 end) as govt_cnt, \
	sum(case when site_type in ('企业') then 1 else 0 end) as company_cnt, \
	sum(case when site_type in ('头条') then 1 else 0 end) as headline_cnt \
	from media \
    group by company_id, substring(publish_time,1,4) || substring(publish_time,5,2);"

def cluster_data(df_input):
    #data = pd.DataFrame(df_input.iloc[10:-10,])
    data = df_input.fillna(method='ffill')

    # cluster model
    # exclude company_id & report_key
    X = pd.DataFrame(data, columns=input_column[:-1])
    cluster = cl.AgglomerativeClustering(n_clusters=num_clusters, affinity='euclidean') # manhattan, cosine,euclidean
    cluster.fit(X)
    data['cluster'] = pd.Series(cluster.labels_, index=data.index)
    return data

def baseline_model(neurons, inputs):
    # create model
    # softmax, elu, softplus, softsign,tanh
    model = Sequential()
    model.add(Dense(neurons, input_dim=inputs, kernel_initializer ='uniform', activation='softsign'))
    model.add(Dense(int(neurons/2), kernel_initializer ='uniform', activation='softplus'))
    model.add(Dense(int(neurons/3), kernel_initializer ='uniform', activation='softplus'))
    model.add(Dense(1, kernel_initializer ='uniform', activation='softplus'))
    # Compile model model.predict
    model.compile(loss='mse', optimizer='adam', metrics=['accuracy'])
    #model.compile(loss='mean_squared_error', optimizer='adam') #Keras 1.0
    return model
      
if __name__ == "__main__":
    print ('Program starts at: '+datetime.datetime.now().strftime("%Y%m%d %H:%M:%S"))
    if len(sys.argv) < 5:
        print(' media_analysis server usr pwd dbname outfile')
        print('		server - Postgres server')
        print('		outfile - output analysis result')
    else:
        server = sys.argv[1]
        usr = sys.argv[2]
        pwd = sys.argv[3]
        dbname = sys.argv[4]
        util = md.Util()
        df_media = util.qry2df(server, usr, pwd, dbname, qry_text)

        # ********** Positive and negative news' count
        media_data = pd.read_csv('../midas_data/media.csv', dtype = {'company_id':str, 'publish_time':str, 'extend1':str})
        for i in range( len(df_media) ):
            current_company_id = str(df_media.iloc[i]['company_id'])
            current_report_key = str(df_media.iloc[i]['report_key'])
            
            pos_data = media_data[(media_data['company_id'] == current_company_id) \
                              & (media_data['publish_time'] == current_report_key) \
                              & (media_data['extend1'] == '1')]
            neg_data = media_data[(media_data['company_id'] == current_company_id) \
                              & (media_data['publish_time'] == current_report_key) \
                              & (media_data['extend1'] == '-1')]

            df_media.loc[i, 'positive_cnt'] = len(pos_data)
            df_media.loc[i, 'negative_cnt'] = len(neg_data)
            
        # ********** Clustering result
        df_cluster = cluster_data(df_media)
        df_cluster.to_csv('../cluster.csv')
    print ('Program ends at: '+datetime.datetime.now().strftime("%Y%m%d %H:%M:%S")) 
    quit(0)
        
    try:
        print ('try catch block')
    except Exception as e: 
        print ('Program error...')
        print(e)
    finally:
        quit(1)
        