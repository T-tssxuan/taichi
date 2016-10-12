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


# Plat the ap access information for given granularity
def ap_plot_data_info(gran=10):
    data = ap_get_data_group_by_ap(gran)
    plt.figure()
    for key in data:
        data[key].plot()
    plt.show()
    
# Generate the data in the difference format with given granularity
def ap_get_data_by_difference(gran=10):
    data = ap_get_data_group_by_ap(gran)
    return {key: data[key].diff() for key in data}

# process wifi, schedule and gate
def ap_schedule_gate_combine(kind='actual_flt_time', gran = 10):
    '''
    kind: the type of time to get
    gran: the granularity of time for wifi_ap the group
    '''
    # get the ap_wifi data
    ap_data = ap_get_data_group_by_ap(gran)

    # get the gate and area data
    gate_data = pd.read_csv('./data/airport_gz_gates.csv')
    gate_data = gate_data.set_index('BGATE_ID')


    # get the schedule data 
    sche_data = pd.read_csv('./data/airport_gz_flights_chusai_1stround.csv')
    sche_data = sche_data[sche_data['BGATE_ID'].notnull()]
    sche_data = sche_data[sche_data[kind].notnull()]

    # for the BGATE_ID has two element we suppose the later one is valid
    last_fun = lambda x: x[-1]
    sche_data['BGATE_ID'] = sche_data['BGATE_ID'].str.split(',').apply(last_fun)
    sche_data.insert(
            len(sche_data.columns),
            'BGATE_AREA',
            gate_data.loc[sche_data['BGATE_ID']].values
            )

    # transform the time string to datetime object
    fmt = '%Y/%m/%d %H:%M:%S'
    sche_data[kind] = pd.to_datetime( sche_data[kind], format=fmt)
    sche_data = sche_data.set_index(kind).sort_index()

    # convert the Greenwich time to Beijing time
    sche_data.index = sche_data.index + pd.DateOffset(hours=8)
    
    return (ap_data, gate_data, sche_data)

# visualize a given area wifi info mark with the given time epoch
# the y axis is the user of an ap.
def visualize_for_area_with_ap(area, kind, gran=10, color='g'):
    ap_data, gate_data, sche_data = ap_schedule_gate_combine(kind, gran)

    ap_data = {key: ap_data[key] for key in ap_data if key.startswith(area)}

    sche_data = sche_data[sche_data['BGATE_AREA'] == area]
    
    for key in ap_data:
        fig = ap_data[key].plot()
        plt.title(area + "---" + kind + "---" + key)
        ymi, ymax = fig.get_ylim()
        plt.xlim(
                pd.to_datetime('2016-09-11 06:00:00'), 
                pd.to_datetime('2016-09-11 20:00:00')
                )
        fig.vlines(x = sche_data.index, ymin=ymin, ymax=ymax - 1, color=color)
    plt.show()

# visualize the area ap info
def actual_visualize_for_area_with_ap(area, gran=10):
    visualize_for_area_with_ap(area, 'actual_flt_time', gran, 'g')

# visualize the area ap info
def schedule_visualize_for_area_with_ap(area, gran=10):
    visualize_for_area_with_ap(area, 'scheduled_flt_time', gran, 'r')

# the same as previous, except the y-axis is the sum of user in given region
def visualize_for_area_with_sum(area, kind, gran=10, color='g'):
    ap_data, gate_data, sche_data = ap_schedule_gate_combine(kind, gran)

    ap_data = {key: ap_data[key] for key in ap_data if key.startswith(area)}

    flag = False
    sum_data = {}
    for key in ap_data.keys():
        if not flag:
            sum_data = ap_data[key].copy()
            flag = True
        else:
            sum_data = sum_data.add(ap_data[key])

    sche_data = sche_data[sche_data['BGATE_AREA'] == area]
    
    fig = sum_data.plot()
    plt.title(area + "---" + kind)
    plt.xlim(
            pd.to_datetime('2016-09-11 06:00:00'), 
            pd.to_datetime('2016-09-11 20:00:00')
            )
    ymi, ymax = fig.get_ylim()
    fig.vlines(x = sche_data.index, ymin=ymin, ymax=ymax - 1, color=color)
    plt.show()

# visualize the area ap sum info
def actual_visualize_for_area_with_sum(area, gran=10):
    visualize_for_area_with_sum(area, 'actual_flt_time', gran, 'g')

# visualize all area ap sum info
def all_area_actual_visualize_for_area_with_sum(gran=10):
    areas = ['E1', 'E2', 'E3', 'EC', 'T1', 'W1', 'W2', 'W3', 'WC']
    for area in areas:
        visualize_for_area_with_sum(area, 'actual_flt_time', gran, 'g')

# visualize the area ap sum info
def schedule_visualize_for_area_with_sum(area, gran=10):
    visualize_for_area_with_sum(area, 'scheduled_flt_time', gran, 'r')

# visualize all area ap sum info
def all_area_schedule_visualize_for_area_with_sum(gran=10):
    areas = ['E1', 'E2', 'E3', 'EC', 'T1', 'W1', 'W2', 'W3', 'WC']
    for area in areas:
        visualize_for_area_with_sum(area, 'scheduled_flt_time', gran, 'r')
