import pandas as pd
import numpy as np
import sys
import os
from log import debug

def generate_ap_ratio_info(directory):
    debug('generat ap ratio info directory: ' + str(directory))

    path = directory + 'WIFI_AP_Passenger_Records_chusai.csv'
    data = pd.read_csv(path)

    # preprocess data
    del data['timeStamp']

    data['WIFIAPTag'] = data['WIFIAPTag'].str.upper()
    data['WIFIAPTag'] = data['WIFIAPTag'].str.replace(' ', '')
    data['area'] = data['WIFIAPTag'].apply(lambda x: x[0:2])

    # get tag sum
    data = data.groupby(['WIFIAPTag', 'area']).sum()
    data = data.reset_index()

    # get area sum
    area_sum = data.copy()
    del area_sum['WIFIAPTag']
    area_sum = area_sum.groupby('area').sum()

    # get the ratio in its area
    def get_ratio(x):
        return x[2] / area_sum.loc[x[1], 'passengerCount']

    data['ratio'] = data.apply(get_ratio, axis=1)

    del data['passengerCount']

    # write to file
    data.to_csv(
    './info/ap_ratio_data.csv', 
    columns=['area', 'WIFIAPTag', 'ratio'], 
    index=False
    )
    return data

if __name__ == '__main__':
    directory = './data1/'
    if len(sys.argv) >= 2 and os.path.exists(sys.argv[1]):
        directory = sys.argv[1]
    generate_ap_ratio_info(directory)
