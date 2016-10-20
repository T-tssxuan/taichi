import pandas as pd
import numpy as np


def generate_base_data(directory, epoch):
    path = derictory + 'WIFI_AP_Passenger_Records_chusai.csv'

    base_data = pd.read_csv(path)
    fmt = '%Y-%m-%d-%H-%M-%S'
    base_data['timeStamp'] = pd.to_datetime(base_data['timeStamp'], format=fmt)
    base_data['WIFIAPTag'] = base_data['WIFIAPTag'].str.upper().replace(' ', '')

    base_data = base_data.groupby(
            ['WIFIAPTag', pd.Grouper(key='timeStamp', freq='1Min')]
            ).sum()
    base_data = base_data.reset_index()

    offset = pd.DateOffset(minutes=-1)
    time = epoch + offset
    base_data = base_data[base_data['timeStamp'] == time]

    base_data['area'] = base_data['WIFIAPTag'].apply(lambda x: x[0:2])

    base_data.to_csv(
    './info/base_data.csv', 
    columns=['area', 'WIFIAPTag', 'passengerCount'],
    index=False
    )

if __name__ == '__main__':
    directory = './data1/'
    epoch = pd.to_datetime('2016/09/25 14:59:00')
    if len(sys.argv) >= 2 and os.path.exists(sys.argv[1]):
        directory = sys.argv[1]

    generate_base_data(directory, epoch)
