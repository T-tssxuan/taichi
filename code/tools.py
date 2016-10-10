import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib

def get_data():
    # Read data from csv file and process the data to a approprioate format
    # 
    wifi_ap = pd.read_csv('./data/WIFI_AP_Passenger_Records_chusai_1stround.csv')
    fmt = '%Y-%m-%d-%H-%M-%S'
    wifi_ap['timeStamp'] = pd.to_datetime(wifi_ap['timeStamp'], format=fmt)
    wifi_ap = wifi_ap.set_index('WIFIAPTag')
    wifi_ap = wifi_ap.groupby(wifi_ap.index)
    granularity = '10Min'
    new_wifi_ap = [
            wifi_ap.get_group(key).set_index('timeStamp')
            for key in wifi_ap.groups.keys()
            ]
    new_wifi_ap = [
            ap.groupby(pd.TimeGrouper(granularity)).aggregate(np.sum) 
            for ap in new_wifi_ap
            ]
    return new_wifi_ap


def for_wifi_ap():
    data = get_data()
    plt.figure()
    for ele in data:
        ele.plot()
    plt.show()
    
def for_deviation_calculate():
    data = get_data()
