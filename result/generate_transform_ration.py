import pandas as pd
import numpy as np
import os
import sys
import time

ap_data = 0
in_data = 0
out_data = 0
pure_data = 0
rst_data = 0
def generate_transform_ration(directory):
    print('generate transform ration')
    
    format = '%Y-%m-%d-%H-%M-%S'
    path = directory + 'WIFI_AP_Passenger_Records_chusai.csv'
    ap_data = pd.read_csv(path)
    ap_data.columns = ['tag', 'num', 'timeStamp']
    del ap_data['tag']
    ap_data['timeStamp'] = pd.to_datetime(ap_data['timeStamp'], format=format)
    ap_data = ap_data.groupby(pd.Grouper(key='timeStamp', freq='1Min')).sum()
    ap_data = ap_data.sort_index()
    ap_data = ap_data.diff()
    ap_data = ap_data.reset_index()
    ap_data = ap_data.groupby(pd.Grouper(key='timeStamp', freq='10Min')).sum()
    ap_data = ap_data.reset_index()

    path = './info/checkin_sum_predict.csv'
    in_data = pd.read_csv(path)
    in_data['timeStamp'] = pd.to_datetime(in_data['timeStamp'])
    in_data = in_data.set_index('timeStamp')

    path = './info/output_sum_predict.csv'
    out_data = pd.read_csv(path)
    out_data['timeStamp'] = pd.to_datetime(out_data['timeStamp'])
    out_data = out_data.set_index('timeStamp')

    pure_data = in_data.subtract(out_data)

    def func(x):
        return x['num'] / pure_data.loc[x['timeStamp'], 'num']

    rst_data = ap_data.apply(func, axis=1)
    return (ap_data, in_data, out_data, rst_data)


if __name__ == '__main__':
    directory = './data1/'
    if len(sys.argv) >= 2 and os.path.exists(sys.argv[1]):
        directory = sys.argv[1]
    ap_data, in_data, out_data, rst_data = generate_transform_ration(directory)
