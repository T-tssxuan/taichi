import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib

init_ap_data = pd.read_csv('./data/WIFI_AP_Passenger_Records_chusai_1stround.csv')

# Read data from csv file and make the data to an appropriate format
def ap_get_data_group_by_ap(gran=10):
    wifi_ap = init_ap_data.copy()
    fmt = '%Y-%m-%d-%H-%M-%S'
    wifi_ap['timeStamp'] = pd.to_datetime(wifi_ap['timeStamp'], format=fmt)
    wifi_ap = wifi_ap.set_index('WIFIAPTag')
    wifi_ap = wifi_ap.groupby(wifi_ap.index)
    granularity = str(gran) + 'Min'
    new_wifi_ap = {
            key: wifi_ap.get_group(key).set_index('timeStamp').sort_index()
            for key in wifi_ap.groups.keys()
            }
    new_wifi_ap = {
            key: new_wifi_ap[key].groupby(pd.TimeGrouper(granularity)).aggregate(np.sum) 
            for key in new_wifi_ap.keys()
            }
    return new_wifi_ap

def visualize_area_ap_time_variation(area, gran=10):
    ap_data = ap_get_data_group_by_ap(gran)
    ap_data = {key: ap_data[key] for key in ap_data.keys() if key.startswith(area)}

    sum_data = {}
    flag = False
    for key in ap_data.keys():
        if not flag:
            sum_data = ap_data[key]
            flag = True
        else:
            sum_data = sum_data.add(ap_data[key])

    tmp = [ap_data[key].div(sum_data).values.flatten() for key in ap_data.keys()]
    new_data = pd.DataFrame(
            np.array(tmp).transpose(), 
            columns=ap_data.keys(), 
            index=sum_data.index
            )

    fig = new_data.plot.bar(figsize=(40, 10), stacked=True)
    fig.legend_.remove()
    plt.show()

def visualize_area_ap_time_variation_no_rate(area, gran=10):
    ap_data = ap_get_data_group_by_ap(gran)
    ap_data = {key: ap_data[key] for key in ap_data.keys() if key.startswith(area)}

    sum_data = {}
    flag = False
    for key in ap_data.keys():
        if not flag:
            sum_data = ap_data[key]
            flag = True
        else:
            sum_data = sum_data.add(ap_data[key])

    tmp = [ap_data[key].values.flatten() for key in ap_data.keys()]
    new_data = pd.DataFrame(
            np.array(tmp).transpose(), 
            columns=ap_data.keys(), 
            index=sum_data.index
            )

    fig = new_data.plot.bar(figsize=(120, 10))
    fig.legend_.remove()
    plt.show()

def get_test_data(area, gran=10):
    ap_data = ap_get_data_group_by_ap(gran)
    ap_data = {key: ap_data[key] for key in ap_data.keys() if key.startswith(area)}

    sum_data = {}
    flag = False
    for key in ap_data.keys():
        if not flag:
            sum_data = ap_data[key]
            flag = True
        else:
            sum_data.add(ap_data[key])

    return (ap_data, sum_data)

