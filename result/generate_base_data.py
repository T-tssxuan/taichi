import pandas as pd
import numpy as np

base_data = pd.read_csv('./data/WIFI_AP_Passenger_Records_chusai_1stround.csv')
fmt = '%Y-%m-%d-%H-%M-%S'
base_data['timeStamp'] = pd.to_datetime(base_data['timeStamp'], format=fmt)
base_data['WIFIAPTag'] = base_data['WIFIAPTag'].str.upper()
base_data = base_data.groupby(
        ['WIFIAPTag', pd.Grouper(key='timeStamp', freq='1Min')]
        ).sum()
base_data = base_data.reset_index()
time = pd.to_datetime('2016-09-14 14:59:00')
base_data = base_data[base_data['timeStamp'] == time]
base_data.to_csv('./info/base_data.csv', index=False)
