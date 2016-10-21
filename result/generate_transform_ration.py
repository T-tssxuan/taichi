import pandas as pd
import numpy as np
import os
import sys
import time

def generate_transform_ration(directory):
    print('generate transform ration')
    
    path = directory + 'WIFI_AP_Passenger_Records_chusai.csv'
    ap_data = pd.read_csv(path)

    path = './info/checkin_sum_predict.csv'
    in_data = pd.read_csv(path)

    path = './info/checkin_sum_predict.csv'




if __name__ == '__main__':
    directory = './data1/'
    if len(sys.argv) >= 2 and os.path.exists(sys.argv[1]):
        directory = sys.argv[1]
    generate_flight_passenger_number(directory)
