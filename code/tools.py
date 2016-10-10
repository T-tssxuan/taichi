import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib

def for_wifi_ap():
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
    plt.figure()
    for ele in new_wifi_ap:
        ele.plot()
    plt.show()
