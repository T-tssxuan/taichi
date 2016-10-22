import pandas as pd
import numpy as np
import os
import sys
import time
from log import debug
from datasrc import datasrc

def generate_pure_variation():
    info_dir = datasrc.get_info_dir()

    path = info_dir + 'checkin_predict.csv'
    cin_data = pd.read_csv(path)
    cin_data['timeStamp'] = pd.to_datetime(cin_data['timeStamp'])

    path = info_dir + 'security_predict.csv'
    sin_data = pd.read_csv(path)
    sin_data['timeStamp'] = pd.to_datetime(sin_data['timeStamp'])

    wcin_data = cin_data.copy()
    wsin_data = sin_data.copy()
    del wcin_data['area']
    del wsin_data['area']
    wcin_data = wcin_data.groupby('timeStamp').sum()
    wsin_data = wsin_data.groupby('timeStamp').sum()

    wpure_data = wcin_data.subtract(wsin_data)
    wpure_data = wpure_data.reset_index()
    wpure_data['area'] = pd.Series(['T1' for i in range(wpure_data.shape[0])])
    wpure_data = wpure_data[['timeStamp', 'num', 'area']]

    path = info_dir + 'output_predict.csv'
    out_data = pd.read_csv(path)
    out_data['timeStamp'] = pd.to_datetime(out_data['timeStamp'])

    sin_data = sin_data.set_index(['timeStamp', 'area'])
    out_data = out_data.set_index(['timeStamp', 'area'])

    pure_data = sin_data.subtract(out_data)
    pure_data = pure_data.reset_index()

    pure_data = pure_data.append(wpure_data)

    ratio = datasrc.get_wifi_ratio()
    pure_data['num'] = pure_data['num'] * ratio

    pure_data.to_csv(
            info_dir + 'variation_data.csv', 
            columns=['timeStamp', 'num', 'area'],
            index=False
            )
    return (sin_data, out_data, pure_data, wpure_data)

if __name__ == '__main__':
    sin_data, out_data, ipure_data, wpure_data = generate_pure_variation()
