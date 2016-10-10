import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib

# Read data from csv file and process the data to an appropriate format
def ap_get_data_group_by_ap(gran=10):
    wifi_ap = pd.read_csv('./data/WIFI_AP_Passenger_Records_chusai_1stround.csv')
    fmt = '%Y-%m-%d-%H-%M-%S'
    wifi_ap['timeStamp'] = pd.to_datetime(wifi_ap['timeStamp'], format=fmt)
    wifi_ap = wifi_ap.set_index('WIFIAPTag')
    wifi_ap = wifi_ap.groupby(wifi_ap.index)
    granularity = str(gran) + 'Min'
    new_wifi_ap = [
            wifi_ap.get_group(key).set_index('timeStamp')
            for key in wifi_ap.groups.keys()
            ]
    new_wifi_ap = [
            ap.groupby(pd.TimeGrouper(granularity)).aggregate(np.sum) 
            for ap in new_wifi_ap
            ]
    return new_wifi_ap


# Plat the ap access information for given granularity
def ap_plot_data_info(gran=10):
    data = ap_get_data_group_by_ap(gran)
    plt.figure()
    for ele in data:
        ele.plot()
    plt.show()
    
# Generate the data in the difference format with given granularity
def ap_get_data_by_difference(gran=10):
    data = ap_get_data_group_by_ap(gran)

