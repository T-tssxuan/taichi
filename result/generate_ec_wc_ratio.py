import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys
import os
from log import debug

def generate_ec_wc_ratio(directory):
    debug('generate ec wc ratio')
    path = directory + 'WIFI_AP_Passenger_Records_chusai.csv'
    ap_data = pd.read_csv(path)
    ap_data.columns = ['tag', 'num', 'timeStamp']

    ap_data['tag'] = ap_data['tag'].str.upper()
    ap_data['tag'] = ap_data['tag'].str.replace(' ', '')
    format = '%Y-%m-%d-%H-%M-%S'
    ap_data['timeStamp'] = pd.to_datetime(ap_data['timeStamp'], format=format)

    ap_data['area'] = ap_data['tag'].str[0:2]
    del ap_data['tag']

    ap_data = ap_data.groupby(
            ['area', pd.Grouper(key='timeStamp', freq='10Min')]
            ).sum()
    ap_data = ap_data.reset_index()
    sum_data = ap_data.copy()

    ap_data = ap_data.groupby('area');

    del sum_data['area']
    sum_data = sum_data.groupby('timeStamp').sum()

    rst = {}
    for key in ap_data.groups:
        tmp = ap_data.get_group(key)
        del tmp['area']
        rst[key] = ap_data.get_group(key).divide(sum_data)

    return rst

if __name__ == '__main__':
    directory = './data1/'
    if len(sys.argv) >= 2 and os.path.exists(sys.argv[1]):
        directory = sys.argv[1]
    rst = generate_ec_wc_ratio(directory)


