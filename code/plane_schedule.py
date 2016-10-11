import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib

fmt = '%Y/%m/%d %H:%M:%S'
sche_data = pd.read_csv('./data/airport_gz_flights_chusai_1stround.csv')

def sche_remove_nan_data():
    data = sche_data.loc[pd.isnull(sche_data['actual_flt_time']) == False]
    return data

def sche_get_delay_stat():
    data = sche_remove_nan_data()
    data['scheduled_flt_time'] = pd.to_datetime(
            data['scheduled_flt_time'], fmt = fmt
            )
    data['actual_flt_time'] = pd.to_datetime(
            data['actual_flt_time'], fmt = fmt
            )
    stat = data['actual_flt_time'] - data['scheduled_flt_time'];
    stat.reset_index()
    stat.columns = ['delay']
    stat = stat.groupby(stat['delay']).count;
