import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

directory = './data1/'

path = directory + 'airport_gz_flights_chusai.csv'
flt_data = pd.read_csv(path)
flt_data.columns = ['fid', 'sft', 'aft', 'gid']
flt_data['fid'] = flt_data['fid'].str.upper()
flt_data['fid'] = flt_data['fid'].str.replace(' ', '')
flt_data['sft'] = pd.to_datetime(flt_data['sft'])
flt_data['aft'] = pd.to_datetime(flt_data['aft'])

path = directory + 'airport_gz_security_check_chusai.csv'
sec_data = pd.read_csv(path)
sec_data.columns = ['pid', 'st', 'fid']
sec_data['fid'] = sec_data['fid'].str.upper()
sec_data['fid'] = sec_data['fid'].str.replace(' ', '')
sec_data['st'] = pd.to_datetime(sec_data['st'])

path = directory + 'airport_gz_departure_chusai.csv'
check_data = pd.read_csv(path)
check_data.columns = ['pid', 'fid', 'ft', 'ct']
check_data['fid'] = check_data['fid'].str.upper()
check_data['fid'] = check_data['fid'].str.replace(' ', '')
check_data['ft'] = pd.to_datetime(check_data['ft'])
check_data['ct'] = pd.to_datetime(check_data['ct'])


def check_in_missed_schedule():
    flt = flt_data.set_index('fid')
    for ele in sec_data.iterrows():

