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

        path = directory + 'airport_gz_flights_chusai.csv'
        sdata = pd.read_csv(path)
        del sdata['actual_flt_time']
        del sdata['BGATE_ID']
        sdata.columns = ['fid', 'sft']
        sdata['fid'] = sdata['fid'].str.upper()
        sdata['fid'] = sdata['fid'].str.replace(' ', '')
        sdata['sft'] = pd.to_datetime(sdata['sft'])
        sdata = sdata.set_index('fid')
        self.sdata = sdata

    def train(self, start, end):
        train_data = self.__get_train_data()
        train_result = [[train_data[co].mean(), train_data[co].std()] 
                for co in train_data.columns]
        
        self.train_data = train_data
        self.train_result = train_result

    # start/end: YYYY/MM/DD HH:MM:SS
    def predict(self, start, end):
        start = pd.to_datetime(start)
        end = pd.to_datetime(end)

        passenger = pd.read_csv('./info/flight_passenger_num.csv')
        passenger.columns = ['fid', 'num']
        passenger['fid'] = passenger['fid'].str.replace(' ', '')
        passenger = passenger.set_index('fid')

        # get the mean and the std of the flight passenger num to fill the blank
        std = self.passenger.std()
        mean = self.passenger.mean()

        def get_number(x):
            if x in passenger.index:
                return passenger.loc[x, 'num']
            else:
                # fill the empty data with the mean and std
                tmp = std * np.random.randn() + mean
                # tmp = 0
                if tmp < 0:
                    tmp = 1
                elif tmp > 300:
                    tmp = 300
                return tmp

        def gen_total(x):
            before = pd.DateOffset(hours=-2)
            after = pd.DateOffset(hours=5)
            
            before_plane = self.sdata[self.sdata > x + before & self.sdata < x]
            after_plane = self.sdata[self.sdata < x + after & self.sdata > x]
            

        
        rst = pd.date_range(start, end, freq='1Min')

    def __get_train_data(self):
        data = self.cdata.copy()

        idx = 0

        before = pd.DateOffset(hours=-5)
        after = pd.DateOffset(hours=2)
        data = data.groupby(['fid', 'ft'])

        rst = pd.DataFrame()

        for fid, ft in data.groups:
            sub_data = data.get_group((fid, ft))
            sub_data = sub_data[sub_data['ct'] >= ft + before]
            sub_data = sub_data[sub_data['ct'] <= ft + after]

            tmp_idx = pd.date_range(ft + before, ft + after, freq='1Min')
            tmp = pd.Series([0 for i in range(len(tmp_idx))], index=tmp_idx)

            del sub_data['ft']
            del sub_data['fid']

            total = sub_data.shape[0]
            if total == 0:
                continue

            sub_data = sub_data.groupby(pd.Grouper(key='ct', freq='1Min')).size()
            del sub_data.index.name

            sub_data = tmp.add(sub_data)
            sub_data = sub_data.fillna(0)
            sub_data = sub_data.divide(total)

            sub_data = pd.DataFrame([sub_data.values], index=[idx])

            rst = pd.concat([rst, sub_data])
            idx += 1

        return rst

ip = input_predict('./data1/')
ip.train('', '')
