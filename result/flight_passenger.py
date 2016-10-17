import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

data = pd.read_csv('./data/airport_gz_departure_chusai_1stround.csv')
del data['passenger_ID2']
data['flight_ID'] = data['flight_ID'].str.replace(' ', '')
data['flight_time'] = pd.to_datetime(data['flight_time'])
data['checkin_time'] = pd.to_datetime(data['checkin_time'])

def replace_flight_time_with_checkin_time(x):
    if pd.isnull(x[1]):
        x[1] = x[2]
    return x
data = data.apply(replace_flight_time_with_checkin_time, axis=1)
del data['checkin_time']

get_day = lambda x: x.day
data['flight_time'] = data['flight_time'].apply(get_day)
data = data[data['flight_time'] != 14]

data = data.groupby(['flight_ID', 'flight_time']).size()
data = data.reset_index()
del data['flight_time']
data = data.groupby('flight_ID').mean()

data = data.reset_index()
data.columns = ['flight_ID', 'num']

data.to_csv(
'./data/flight_passenger_num.csv', 
columns=['flight_ID', 'num'],
index=False
)
