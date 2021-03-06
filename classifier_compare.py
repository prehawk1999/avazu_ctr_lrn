# -*- coding: utf-8 -*-
"""
Created on Sat Mar 18 21:39:07 2017

@author: prehawk
"""

"""
======================================================
Out-of-core classification of  Avazu data
======================================================
wc count for train.csv 40428968
wc count for test.csv   4577465
 Features engineerig
 Features Hasher
 SGD classifier with partial fit
 invscaling with eta0 =4-8
l2 penalty
labels changed in -1,1 as vowpal wabbit

warm on a shuffled file
"""
#%%
# Authors: Elena Cuoco <elena.cuoco@gmail.com>
#
#Avazu competitor usign pandas and scikit library
import numpy as np
import pandas as pd
from datetime import datetime, date, time
from sklearn.linear_model import SGDClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss
from sklearn import  cross_validation
from sklearn.feature_extraction import FeatureHasher
from sklearn import preprocessing 
from sklearn.pipeline import Pipeline

#joblib library for serialization
from sklearn.externals import joblib
#json library for settings file


##Read configuration parameters
train_file='f:\\data\\avazu_ctr\\train.csv'
MODEL_PATH='f:\\gitroot\\avazu_ctr_lrn\\solutions\\elenacuoco\\'

warm_file='f:\\data\\avazu_ctr\\start.csv'
seed= int(3217)


#%%
###############################################################################
# Main
###############################################################################
chunk_size=int(4096)
header=['id','click','hour','C1','banner_pos','site_id','site_domain','site_category','app_id','app_domain','app_category','device_id'\
        ,'device_ip','device_model','device_type','device_conn_type','C14','C15','C16','C17','C18','C19','C20','C21']
 
#preprocessing
preproc =Pipeline([('fh',FeatureHasher( n_features=2**27,input_type='string', non_negative=False))])
# 
def clean_data(data):
    y_train=data['click']##for Vowpal Wabbit
    data['app']=data['app_id'].values+data['app_domain'].values+data['app_category'].values
    data['site']=data['site_id'].values+data['site_domain'].values+data['site_category'].values
    data['device']= data['device_id'].values+data['device_ip'].values+data['device_model'].values+(data['device_type'].values.astype(str))+(data['device_conn_type'].values.astype(str))
    data['type']=data['device_type'].values +data['device_conn_type'].values 
    data['iden']=data['app_id'].values +data['site_id'].values +data['device_id'].values
    data['domain']=data['app_domain'].values +data['site_domain'].values
    data['category']=data['app_category'].values+data['site_category'].values
    data['pS1']=data['C1'].values.astype(str)+data['app_id']
    data['pS2']= data['C14'].values+data['C15'].values+data['C16'].values+data['C17'].values
    data['pS3']=data['C18'].values+data['C19'].values+data['C20'].values+data['C21'].values
    data['sum']=data['C1'].values+data['C14'].values+data['C15'].values+data['C16'].values+data['C17'].values\
    +data['C18'].values+data['C19'].values+data['C20'].values+data['C21'].values
    data['pos']= data['banner_pos'].values.astype(str)+data['app_category'].values+data['site_category'].values 
    data['pS4']=data['C1'].values.astype(int) - data['C20'].values.astype(int)
    data['ps5']=data['C14'].values.astype(int) - data['C21'].values.astype(int)
    
    data['hour']=data['hour'].map(lambda x: datetime.strptime(str(x),"%y%m%d%H"))
    data['dayoftheweek']=data['hour'].map(lambda x:  x.weekday())
    data['day']=data['hour'].map(lambda x:  x.day)
    data['hour']=data['hour'].map(lambda x:  x.hour)
    day=data['day'].values[len(data)-1]
    clean=data.drop(['id','click'], axis=1)#remove id and click columns
    X_dict=np.asarray(clean.astype(str))
    y_train = np.asarray(y_train).ravel()
   ######## preprocessing
    
    X_train=preproc.fit_transform(X_dict)
    
    
    return day,y_train,X_train


#%%

# data = pd.read_csv(warm_file)
warm_reader = pd.read_table(warm_file, sep=',', chunk_size=CHUNK_SIZE)
# days, y_train, X = clean_data(data)

from sklearn.cross_validation import train_test_split
X_col = data.columns.tolist()
X_col.remove('click')

from sklearn.preprocessing import OneHotEncoder
enc = OneHotEncoder()
enc
X_train, X_test, y_train, y_test = train_test_split(data[X_col], data['click'], test_size=0.3, random_state=0) # 为了看模型在没有见过数据集上的表现，随机拿出数据集中30%的部分做测试
#%%

#classifier
cls= SGDClassifier(loss='log', n_iter=200, alpha=.0000001, penalty='l2',\
learning_rate='invscaling',power_t=0.5,eta0=4.0,shuffle=True,n_jobs=-1,random_state=seed)

cls.partial_fit(X_train, y_train,classes = np.array([0, 1]))
y_pred = cls.predict_proba(X_test)
LogLoss=log_loss(y_test, y_pred)
print('log_loss:%f' % LogLoss)