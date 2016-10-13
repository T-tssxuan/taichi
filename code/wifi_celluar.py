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

    sum_value = 0
    ratio_data = {}
    flag = False
    for key in ap_data.keys():
        ratio_data[key] = ap_data[key].sum().values[0]
        sum_value += ratio_data[key]

    ratio_data = {key: ratio_data[key] / sum_value for key in ratio_data.keys()}

    fig = new_data.plot.bar(figsize=(80, 8), stacked=True)
    x_min, x_max = fig.get_xlim()
    pos = 0.0
    for key in ratio_data.keys():
        pos += ratio_data[key]
        fig.hlines(y = pos, xmin = x_min, xmax = x_max)
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

    fig = new_data.plot.bar(figsize=(80, 8), stacked=True)
    fig.legend_.remove()
    plt.show()

def get_area_celluar_ratio(area, gran=10):
    ap_data = ap_get_data_group_by_ap(gran)
    ap_data = {key: ap_data[key] for key in ap_data.keys() if key.startswith(area)}

    sum_data = 0
    ratio_data = {}
    flag = False
    for key in ap_data.keys():
        ratio_data[key] = ap_data[key].sum().values[0]
        sum_data += ratio_data[key]

    ratio_data = {key: ratio_data[key] / sum_data for key in ratio_data.keys()}

    return ratio_data

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

def visualize_stair_ap_time_variation(area, gran=10):
    ap_data = ap_get_data_group_by_ap(gran)
    ap_data = {key: ap_data[key] for key in ap_data.keys() if key.startswith(area)}

    new_data = {}
    sum_value = 0
    sum_set = False
    for i in range(1, 4):
        idx = area + '-' + str(i)
        flag = False
        for key in ap_data.keys():
            if key.startswith(idx):
                if not flag:
                    flag = True
                    new_data[idx] = ap_data[key]
                else:
                    new_data[idx] = new_data[idx].add(ap_data[key])
        if not sum_set:
            sum_set = True
            sum_value = new_data[idx]
        else:
            sum_value = sum_value.add(new_data[idx])
        
    rate_data = {key: new_data[key].div(sum_value)['passengerCount'] for key in new_data.keys()}
    rate_data = pd.DataFrame.from_dict(rate_data)
    
    primary_data = {key: new_data[key]['passengerCount'] for key in new_data.keys()}
    primary_data = pd.DataFrame.from_dict(primary_data)
    
    fig = rate_data.plot.bar(figsize=(80, 8), stacked=True)
    x_min, x_max = fig.get_xlim()
    fig.legend_.remove()
    plt.show()
    
    fig = primary_data.plot.bar(figsize=(80, 8), stacked=True)
    x_min, x_max = fig.get_xlim()
    fig.legend_.remove()
    plt.show()

