import pandas as pd
import numpy as np
import sys
import os
from generate_ap_ratio_info import generate_ap_ratio_info
from log import debug


def generate_base_data(directory, epoch):
    debug('generate the base data directory: ' + str(directory) + ' epoch: ' +
            str(epoch))

    epoch = pd.to_datetime(epoch)
    path = directory + 'WIFI_AP_Passenger_Records_chusai.csv'

    base_data = pd.read_csv(path)
    fmt = '%Y-%m-%d-%H-%M-%S'
    base_data['timeStamp'] = pd.to_datetime(base_data['timeStamp'], format=fmt)
    base_data['WIFIAPTag'] = base_data['WIFIAPTag'].str.upper()
    base_data['WIFIAPTag'] = base_data['WIFIAPTag'].str.replace(' ', '')

    base_data = base_data.groupby(
            ['WIFIAPTag', pd.Grouper(key='timeStamp', freq='1Min')]
            ).mean()
    base_data = base_data.reset_index()

    offset = pd.DateOffset(minutes=-1)
    time = epoch + offset
    base_data = base_data[base_data['timeStamp'] == time]

    base_data['area'] = base_data['WIFIAPTag'].apply(lambda x: x[0:2])

    # generate each ap user ratio in their area
    debug('generate ap ratio info')
    ap_ratio_data = generate_ap_ratio_info(directory)

    ap_ratio_data = ap_ratio_data.set_index('WIFIAPTag')

    func = lambda x: ap_ratio_data.loc[x, 'ratio']

    base_data['ratio'] = base_data['WIFIAPTag'].apply(func)

    base_data.to_csv(
    './info/base_data.csv', 
    columns=['area', 'WIFIAPTag', 'passengerCount', 'ratio'],
    index=False
    )

if __name__ == '__main__':
    directory = './data1/'
    epoch = pd.to_datetime('2016/09/14 15:00:00')
    if len(sys.argv) >= 2 and os.path.exists(sys.argv[1]):
        directory = sys.argv[1]

    generate_base_data(directory, epoch)
