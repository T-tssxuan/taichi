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
        self.sdata = sdata

        pdata = pd.read_csv('./info/flight_passenger_num.csv')
        pdata.columns = ['fid', 'num']
        pdata['fid'] = passenger['fid'].str.replace(' ', '')
        pdata = passenger.set_index('fid')
        self.pdata = pdata

        # get the mean and the std of the flight passenger num to fill the blank
        self.pstd = pdata.std()
        self.pmean = pdata.mean()

    # start/end: YYYY/MM/DD HH:MM:SS
    def predict(self, start, end):
        start = pd.to_datetime(start)
        end = pd.to_datetime(end)


    def train(self, start, end):
        train_data = self.__get_train_data()
        train_result = [[train_data[co].mean(), train_data[co].std()] 
                for co in train_data.columns]
        
        self.train_data = train_data
        self.train_std = train_data.std()
        self.train_mean = train_data.mean()

        rst = pd.DataFrame()
        for row in self.sdata.iterrows():
            p_num = np.random.randn() * self.pstd + self.pmean
            if row['fid'] in self.pdata.index:
                p_num = self.pdata[row['fid']]

            tmp = self.__spread(row['fid'], row['sft'], p_num)
            rst = rst.append(tmp)

        self.rst = rst


    def __spread(self, fid, sft, p_num):
        before = pd.DateOffset(hours=-5)
        after = pd.DateOffset(hours=2)

        num = np.array([
            np.random.randn() * self.train_std[i] + self.train_mean[i]
            for i in range(len(self.train_std))
            ])
        num = spread * p_num

        time = pd.date_range(sft + before, sft + after, freq='1Min').values
        
        fids = pd.Series([fid for i in range(len(self.train_std))]).values

        rst = pd.Series(np.array([time, fids, num]).transpose())

        return rst


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
