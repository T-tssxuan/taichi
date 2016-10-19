import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

class input_predict:
    '''
    This class is using to predict the input of the airport based on the check 
    in information of the airport.
    '''
    def __init__(self, directory):
        path = directory + 'airport_gz_departure_chusai.csv'
        cdata = pd.read_csv(path)
        del cdata['passenger_ID2']
        cdata.columns = ['fid', 'ft', 'ct']
        cdata['fid'] = cdata['fid'].str.upper()
        cdata['fid'] = cdata['fid'].str.replace(' ', '')
        cdata['ft'] = pd.to_datetime(cdata['ft'])
        cdata['ct'] = pd.to_datetime(cdata['ct'])
        cdata = cdata[pd.notnull(cdata['ft'])]
        cdata = cdata[pd.notnull(cdata['ct'])]
        self.cdata = cdata

    def train(self, start, end):
        self.train_data = self.__get_train_data()


    def __get_train_data(self):
        data = self.cdata.copy()

        idx = 0

        offset = pd.DateOffset(hours=-5)
        data = data.groupby(['fid', 'ft'])

        rst = pd.DataFrame()

        for fid, ft in data.groups:
            sub_data = data.get_group((fid, ft))
            sub_data = sub_data[sub_data['ct'] >= ft + offset]

            tmp_idx = pd.date_range(ft + offset, ft, freq='2Min')
            tmp = pd.Series([0 for i in range(len(tmp_idx))], index=tmp_idx)

            del sub_data['ft']
            del sub_data['fid']

            total = sub_data.shape[0]
            sub_data = sub_data.groupby(pd.Grouper(key='ct', freq='2Min')).size()
            del sub_data.index.name

            print(type(sub_data))
            print(type(tmp))
            print(sub_data.head())
            print(tmp.head())

            sub_data = tmp.add(sub_data)
            sub_data = sub_data.fillna(0)
            sub_data = sub_data.divide(total).cumsum()

            print(sub_data.head())

            sub_data = pd.DataFrame([sub_data.values], index=idx)

            rst = pd.concat([rst, sub_data])
            idx += 1

        return rst

ip = input_predict('./data1/')
ip.train('', '')
