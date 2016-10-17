import pandas as pd
import numpy as np

data = pd.read_csv('./data/WIFI_AP_Passenger_Records_chusai_1stround.csv')
del data['timeStamp']

data['WIFIAPTag'] = data['WIFIAPTag'].str.upper().replace(' ', '')
data['area'] = data['WIFIAPTag'].apply(lambda x: x[0:2])

data = data.groupby(['WIFIAPTag', 'area']).sum()
