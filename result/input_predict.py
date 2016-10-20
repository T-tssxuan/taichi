import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

class input_predict:
    '''
    This class is using to predict the input of the airport based on the check 
    in information of the airport.
    '''
    def __init__(self, directory):
        self.directory = directory
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
        sdata.columns = ['fid', 'sft', 'gate']
        sdata['fid'] = sdata['fid'].str.upper()
        sdata['fid'] = sdata['fid'].str.replace(' ', '')
        sdata['sft'] = pd.to_datetime(sdata['sft'])
        sdata['sft'] = sdata['sft'].add(pd.DateOffset(hours=8))
        self.sdata = sdata
        self.__bind_area_for_fid()
        del self.sdata['gate']

        pdata = pd.read_csv('./info/flight_passenger_num.csv')
        pdata.columns = ['fid', 'num']
        pdata['fid'] = pdata['fid'].str.replace(' ', '')
        pdata = pdata.set_index('fid')
        self.pdata = pdata

        # get the mean and the std of the flight passenger num to fill the blank
        self.pstd = pdata.std()[0]
        self.pmean = pdata.mean()[0]

    # start/end: YYYY/MM/DD HH:MM:SS
    def get_predict_area(self, start, end, gran=10):
        start = pd.to_datetime(start)
        end = pd.to_datetime(end)

        tmp = self.rst[
                self.rst['timeStamp'] >= start & self.rst['timeStamp'] <= end
                ]
        tmp = tmp.groupby(
                [pd.Grouper(key='timeStamp', freq=gran), 'area']
                ).sum()

        tmp = tmp.reset_index()
        return tmp


    def get_predict_sum(self, start, end, gran=10):
        start = pd.to_datetime(start)
        end = pd.to_datetime(end)
        gran = str(gran) + 'Min'

        tmp = self.rst.copy()
        del tmp['area']

        tmp = tmp[tmp['timeStamp'] >= start & tmp['timeStamp'] <= end]

        tmp = tmp.groupby(pd.Grouper(key='timeStamp', freq=gran)).sum()
        
        tmp = tmp.reset_index()

        return tmp


    def train(self, start, end):
        train_data = self.__get_train_data()
        train_result = [[train_data[co].mean(), train_data[co].std()] 
                for co in train_data.columns]
        
        self.train_result = train_result
        self.train_data = train_data
        self.train_std = train_data.std()
        self.train_mean = train_data.mean()

        rst = pd.DataFrame()
        for idx, row in self.sdata.iterrows():
            p_num = np.random.randn() * self.pstd + self.pmean
            if row['fid'] in self.pdata.index:
                p_num = self.pdata.loc[row['fid'], 'num']

            tmp = self.__spread(row['sft'], row['area'], p_num)
            rst = rst.append(tmp)

        rst['timeStamp'] = pd.to_datetime(rst['timeStamp'])
        rst = rst.groupby(['timeStamp', 'area']).sum()
        rst = rst.sort_index()
        rst = rst.reset_index()
        rst.to_csv('./info/input_predict', ['timeStamp', 'area', 'num'], index=True)
        self.rst = rst

    def __spread(self, sft, area, p_num):
        # print(str(p_num) + ' ' + str(type(p_num)))
        # print(str(sft))
        # print(str(area))
        before = pd.DateOffset(hours=-5)
        after = pd.DateOffset(hours=2)

        num = np.array([
            np.random.randn() * self.train_std[i] + self.train_mean[i]
            for i in range(len(self.train_std))
            ])
        num = num * p_num

        time = pd.date_range(sft + before, sft + after, freq='1Min').values
        
        areas = pd.Series([area for i in range(len(self.train_std))]).values

        columns = ['timeStamp', 'area', 'num']

        rst = pd.DataFrame(
            np.array([time, areas, num]).transpose(), 
            columns=columns
            )

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
    
    def __bind_area_for_fid(self):
        print('fill area according to the flight gate')
        gate = pd.read_csv(self.directory + './airport_gz_gates.csv')
        gate.columns = ['gate', 'area']
        gate['gate'] = gate['gate'].str.upper()
        gate['gate'] = gate['gate'].str.replace(' ', '')
        gate['area'] = gate['area'].str.upper()
        gate['area'] = gate['area'].str.replace(' ', '')
        gate = gate.set_index('gate')

        tmp = ['E1', 'E2']
        def func(x):
            if x in gate.index:
                return gate.loc[x, 'area']
            else:
                return tmp[np.random.randint(2)]
        self.sdata['area'] = self.sdata['gate'].apply(func)

if __name__ == '__main__':
    ip = input_predict('./data1/')
    ip.train('', '')
