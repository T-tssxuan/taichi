import pandas as pd
import numpy as np
import os
import sys
import time

def generate_pure_variation(directory):
    path = './info/checkin_predict.csv'
    cin_data = pd.read_csv(path)
    cin_data['timeStamp'] = pd.to_datetime(cin_data['timeStamp'])

    path = './info/security_predict.csv'
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

    path = './info/output_predict.csv'
    out_data = pd.read_csv(path)
    out_data['timeStamp'] = pd.to_datetime(out_data['timeStamp'])

    sin_data = sin_data.set_index(['timeStamp', 'area'])
    out_data = out_data.set_index(['timeStamp', 'area'])

    pure_data = sin_data.subtract(out_data)
    pure_data = pure_data.reset_index()

    pure_data = pure_data.append(wpure_data)

    pure_data['num'] = pure_data['num'] * 0.15

    pure_data.to_csv(
            './info/variation_data.csv', 
            columns=['timeStamp', 'num', 'area'],
            index=False
            )
    return (sin_data, out_data, pure_data, wpure_data)

if __name__ == '__main__':
    directory = './data1/'
    if len(sys.argv) >= 2 and os.path.exists(sys.argv[1]):
        directory = sys.argv[1]
    sin_data, out_data, ipure_data, wpure_data = generate_pure_variation(directory)
