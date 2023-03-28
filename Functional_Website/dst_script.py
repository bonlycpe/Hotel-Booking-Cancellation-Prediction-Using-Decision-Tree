import csv
import os
from flask import Flask, render_template
from collections import defaultdict
from datetime import datetime
from decimal import Decimal
import pandas as pd
import numpy as np
import missingno as msno

import warnings
warnings.filterwarnings('ignore')

from sklearn.tree import DecisionTreeClassifier


def input_validation(filename):

    FeatureList = [
    'hotel',
    'lead_time',
    'arrival_date_month',
    'arrival_date_week_number',
    'arrival_date_day_of_month',
    'stays_in_weekend_nights',
    'stays_in_week_nights',
    'adults',
    'children',
    'babies',
    'meal',
    'market_segment',
    'distribution_channel',
    'is_repeated_guest',
    'previous_cancellations',
    'previous_bookings_not_canceled',
    'reserved_room_type',
    'deposit_type',
    'agent',
    'company',
    'customer_type',
    'adr',
    'required_car_parking_spaces',
    'total_of_special_requests',
    'reservation_status_date',
    'name'
    ]

    df = pd.read_csv(filename)

    df_columns = list(df.columns)
    for feature in FeatureList:
        if feature not in df_columns:
            return False
        
    return True


###ใช้แก้ข้อมูลพวก NULL ใน Dataframe
def FillNA(df):
    # แยกค่า NULL
    null = pd.DataFrame({'Null Values' : df.isna().sum(), 'Percentage Null Values' : (df.isna().sum()) / (df.shape[0]) * (100)})

    # filling null values with zero
    df.fillna(0, inplace = True)

    # ทั้ง 3 collumn จะเป็น 0 หมด  ไม่ได้
    filter = (df.children == 0) & (df.adults == 0) & (df.babies == 0)

    # เอา Record ที่ 3 column เป็น 0 ออก
    df = df[~filter]
    
    return df


###ใช้กรอก Column ให้เหลือเฉพาะที่ต้องการๅ
def FilterColumn(df):
    
    FeatureList = [
    'hotel',
    'lead_time',
    'arrival_date_month',
    'arrival_date_week_number',
    'arrival_date_day_of_month',
    'stays_in_weekend_nights',
    'stays_in_week_nights',
    'adults',
    'children',
    'babies',
    'meal',
    'market_segment',
    'distribution_channel',
    'is_repeated_guest',
    'previous_cancellations',
    'previous_bookings_not_canceled',
    'reserved_room_type',
    'deposit_type',
    'agent',
    'company',
    'customer_type',
    'adr',
    'required_car_parking_spaces',
    'total_of_special_requests',
    'reservation_status_date',
    'name'
    ]

    ###   https://www.sciencedirect.com/science/article/pii/S2352340918315191
    
    
    clist = []
    for c in df:
        if(c not in FeatureList):
            df = df.drop(columns=c)
    
    
    for c in df:
        clist.append(c)
    
    
    clist=clist.sort()
    FeatureList=FeatureList.sort()
    if(clist != FeatureList):
        print("Error : Data doesn't met requiment")
        for c in clist:
            if c not in FeatureList:
                print(c+' not found!')
        return 0
    
    return df


####แปลงข้อมูลใน Dataframe  ทั้งหมด
#-FillNA
#-FileterColumn
#-แปลง Categorical เป็น Label
#-Nomalize ค่าใน Dataframe
#แยก column ชื่่อคนออกมา

#Return DF-X และ DFชื่อคน
def PreProcessingData(df):
    
    dfname = df.copy()
    df.drop(['name'] , axis = 1, inplace = True)
    
    df = FilterColumn(df)
    if (not isinstance(df, pd.DataFrame)):
        return 0
    df = FillNA(df)
    
    
    # creating categorical dataframes
    cat_cols = [col for col in df.columns if df[col].dtype == 'O']
    cat_df = df[cat_cols]

    cat_df['reservation_status_date'] = pd.to_datetime(cat_df['reservation_status_date'])
    cat_df['year'] = cat_df['reservation_status_date'].dt.year
    cat_df['month'] = cat_df['reservation_status_date'].dt.month
    cat_df['day'] = cat_df['reservation_status_date'].dt.day
    cat_df.drop(['reservation_status_date','arrival_date_month'] , axis = 1, inplace = True)
    cat_df['hotel'] = cat_df['hotel'].map({'Resort Hotel' : 0, 'City Hotel' : 1})
    cat_df['meal'] = cat_df['meal'].map({'BB' : 0, 'FB': 1, 'HB': 2, 'SC': 3, 'Undefined': 4})
    cat_df['market_segment'] = cat_df['market_segment'].map({'Direct': 0, 'Corporate': 1, 'Online TA': 2, 'Offline TA/TO': 3,
                                                             'Complementary': 4, 'Groups': 5, 'Undefined': 6, 'Aviation': 7})
    cat_df['distribution_channel'] = cat_df['distribution_channel'].map({'Direct': 0, 'Corporate': 1, 'TA/TO': 2, 'Undefined': 3,
                                                                           'GDS': 4})
    cat_df['reserved_room_type'] = cat_df['reserved_room_type'].map({'C': 0, 'A': 1, 'D': 2, 'E': 3, 'G': 4, 'F': 5, 'H': 6,
                                                                       'L': 7, 'B': 8})
    cat_df['deposit_type'] = cat_df['deposit_type'].map({'No Deposit': 0, 'Refundable': 1, 'Non Refund': 3})
    cat_df['customer_type'] = cat_df['customer_type'].map({'Transient': 0, 'Contract': 1, 'Transient-Party': 2, 'Group': 3})
    cat_df['year'] = cat_df['year'].map({2015: 0, 2014: 1, 2016: 2, 2017: 3})
    
    
    
    
    num_df = df.drop(columns = cat_cols, axis = 1)
    num_df

    # normalizing numerical variables

    num_df['lead_time'] = np.log(num_df['lead_time'] + 1)
    num_df['arrival_date_week_number'] = np.log(num_df['arrival_date_week_number'] + 1)
    num_df['arrival_date_day_of_month'] = np.log(num_df['arrival_date_day_of_month'] + 1)
    num_df['agent'] = np.log(num_df['agent'] + 1)
    num_df['company'] = np.log(num_df['company'] + 1)
    num_df['adr'] = np.log(num_df['adr'] + 1)
    num_df['adr'] = num_df['adr'].fillna(value = num_df['adr'].mean())
    
    
    X = pd.concat([cat_df, num_df], axis = 1)

    return X, dfname


def loadModel(path):
    from joblib import load
    dtc = load(path)
    return dtc


def dst_process(filename):
    name = filename.split('\\')
    name = name[len(name)-1].split('.')
    name = name[0]

    df, dfName = PreProcessingData(pd.read_csv(filename))

    dtc = loadModel(r'./dtc.joblib')  #โหลด Model Decision Tree
    pred = dtc.predict(df)   #Predict ว่ามีโอกาส Cancel   (Return Array)
    pred = pd.DataFrame(pred, columns = ['Status'])  #แปลง Array เป็น df
    df = pd.concat([dfName, pred], axis = 1) #เอาผล pred มาต่อกับ name

    df['Status'] = df['Status'].apply(lambda x: 'Cancel' if x == 1 else 'Not Cancel')

    if "Cancel" in df['Status'].values:
        C = df['Status'].value_counts()["Cancel"]
    else: C=0

    if "Not Cancel" in df['Status'].values:
        N = df['Status'].value_counts()["Not Cancel"]
    else: N=0

    #dfChart = [df['Status'].value_counts()["Cancel"],df['Status'].value_counts()["Not Cancel"]]

    df.to_csv(f"output/result.csv",encoding='utf-8-sig')

    return df,C,N