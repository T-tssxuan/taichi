import pandas as pd
import numpy as np


def generate_ap_ratio_info(directory):
    path = directory + 'WIFI_AP_Passenger_Records_chusai.csv'
    data = pd.read_csv(path)

    # preprocess data
    del data['timeStamp']

    data['WIFIAPTag'] = data['WIFIAPTag'].str.upper().replace(' ', '')
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
