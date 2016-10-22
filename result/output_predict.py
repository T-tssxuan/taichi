import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys
import os
from log import debug

class output_predict:
    '''
    attributes:
        sche: the plane schedule information
        rst: the output predict for each area
        distribute: the area scheduled plane distribute
        empty_count: the number of plane which is not given setting off area 
        date_start: the start of the predict day
        date_end: the end of the predict day 
    dependencies:
        .directory/airport_gz_flights_chusai.csv
        .directory/airport_gz_gates.csv
        ./info/flight_passenger_num.csv
    result:
        ./info/output_predic.csv
    '''
    def __init__(self, start, end, directory):
        debug('output_predict start: ' + str(start) + ' end: ' + str(end) + 
                ' directory: ' + str(directory))

        self.w_ratio = 0.6252504
        self.e_ratio = 0.560917

        debug('output_predict w_ratio: ' + str(self.w_ratio) + 
                ' e_ratio: ' + str(self.e_ratio))

        self.directory = directory
        path = self.directory + 'airport_gz_flights_chusai.csv'

        self.date_start = pd.to_datetime(start)
        self.date_end = pd.to_datetime(end)

        sche = pd.read_csv(path)
        sche.columns = ['fid', 'sft', 'aft', 'gate']
        sche['sft'] = pd.to_datetime(sche['sft'])
        sche['aft'] = pd.to_datetime(sche['aft'])
        sche['fid'] = sche['fid'].str.upper()
        sche['fid'] = sche['fid'].str.replace(' ', '')
        sche['gate'] = sche['gate'].str.replace(' ', '')
        sche['gate'] = sche['gate'].astype(str)
        sche['gate'] = sche['gate'].apply(lambda x: x.split(',')[-1])

        self.sche = sche

        self.__fill_delay_for_without_actual_flt()
        self.__fill_area_according_to_gate()
        self.__fill_passenger_number_according_statistic()

        del self.sche['sft']
        del self.sche['gate']
        del self.sche['fid']

        rst = self.__get_output_predict_for_each_area()

        self.rst = self.__set_ec_wc_num(rst)

        self.rst.to_csv(
                './info/output_predict.csv', 
                columns=['timeStamp', 'num', 'area'],
                index=False
                )

        # output the sum
        gran = '10Min'
        sum_rst = self.rst.copy()
        del sum_rst['area']
        sum_rst = sum_rst.groupby(pd.Grouper(key='timeStamp', freq=gran)).sum()
        sum_rst = sum_rst.reset_index()
        sum_rst.to_csv(
                './info/output_sum_predict.csv',
                columns=['timeStamp', 'num'],
                index=False
                )

    def __set_ec_wc_num(self, rst):
        debug('set EC WC area num')
        tmp = rst.set_index(['timeStamp', 'area'])
        def func(x):
            val = 0
            if x['area'] == 'EC':
                val += tmp.loc[x['timeStamp'], 'E1']['num']
                val += tmp.loc[x['timeStamp'], 'E2']['num']
                val += tmp.loc[x['timeStamp'], 'E3']['num']
                return val * (1 - self.e_ratio)
            elif x['area'] == 'WC':
                val += tmp.loc[x['timeStamp'], 'W1']['num']
                val += tmp.loc[x['timeStamp'], 'W2']['num']
                val += tmp.loc[x['timeStamp'], 'W3']['num']
                return val * (1 - self.w_ratio)
            elif x['area'] == 'W1' or x['area'] == 'W2' or x['area'] == 'W3':
                return x['num'] * self.w_ratio
            else:
                return x['num'] * self.e_ratio

        rst['num'] = rst.apply(func, axis=1)
        return rst

    def get_predict_sum(self, start, end, gran=10):
        '''
        get the predict data with summary of all
        '''
        debug('get the sum predict data')
        start = pd.to_datetime(start)
        end = pd.to_datetime(end)
        gran = str(gran) + 'Min'

        tmp = self.rst.copy()
        del tmp['area']

        tmp = tmp[(tmp['timeStamp'] >= start) & (tmp['timeStamp'] <= end)]

        tmp = tmp.groupby(pd.Grouper(key='timeStamp', freq=gran)).sum()
        
        tmp = tmp.reset_index()

        return tmp

    def __fill_delay_for_without_actual_flt(self):
        debug('fill delay for without actual flight time')
        def delay(x):
            if pd.isnull(x[2]):
                offset = int(18 * np.random.randn() + 22)
                offset = pd.DateOffset(minutes=offset)
                x[2] = x[1] + offset
            return x
        self.sche = self.sche.apply(delay, axis=1)

        set_offset = lambda x: x + pd.DateOffset(hours=8)
        self.sche['sft'] = self.sche['sft'].apply(set_offset)
        self.sche['aft'] = self.sche['aft'].apply(set_offset)
        
    def __fill_area_according_to_gate(self):
        debug('fill area according to the flight gate')
        gate = pd.read_csv(self.directory + './airport_gz_gates.csv')
        gate.columns = ['gate', 'area']
        gate['gate'] = gate['gate'].str.replace(' ', '')
        gate['area'] = gate['area'].str.replace(' ', '')
        gate = gate.set_index('gate')

        tmp = ['E1', 'E2']
        # record the number gate without area
        self.empty_count = 0
        # count each area scheduled plane number
        self.distribute = {'W1': 0, 'W2': 0, 'W3': 0, 'E1': 0, 'E2': 0, 'E3': 0}
        def func(x):
            if x in gate.index:
                self.distribute[gate.loc[x, 'area']] += 1
                return gate.loc[x, 'area']
            else:
                self.empty_count += 1
                return tmp[np.random.randint(2)]
        self.sche['area'] = self.sche['gate'].apply(func)


    def __fill_passenger_number_according_statistic(self):
        debug('fill passenger number according statistic')
        passenger = pd.read_csv('./info/flight_passenger_num.csv')
        passenger.columns = ['fid', 'num']
        passenger['fid'] = passenger['fid'].str.replace(' ', '')
        passenger = passenger.set_index('fid')

        # get the mean and the std of the flight passenger num to fill the blank
        std = passenger.std()['num']
        mean = passenger.mean()['num']

        self.sum_flight = 0
        self.miss_passenger = 0
        self.miss_fid = []
        def get_number(x):
            self.sum_flight += 1
            if x in passenger.index:
                return passenger.loc[x, 'num']
            else:
                self.miss_fid.append(x)
                self.miss_passenger += 1
                # fill the empty data with the mean and std
                tmp = std * np.random.randn() + mean
                return tmp
        self.sche['num'] = self.sche['fid'].apply(get_number)

    def __get_output_predict_for_each_area(self):
        debug('get output predict for each plane')

        columns_name = ['timeStamp', 'num', 'area']

        offset = pd.DateOffset(minutes=20)

        # generate output info for each minutes in the given time range
        rgn = pd.date_range(self.date_start, self.date_end, freq='Min')
        areas = ['W1', 'W2', 'W3', 'E1', 'E2', 'E3', 'EC', 'WC']
        tmp = pd.DataFrame([], columns=columns_name)
        zeros = [0 for i in range(rgn.shape[0])]
        for area in areas:
            foo = [area for i in range(rgn.shape[0])]
            pad = np.array([rgn, zeros, foo]).transpose()
            tmp = tmp.append(pd.DataFrame(pad, columns=columns_name))

        # the spread function
        def gen_num(idx, num):
            return num / 20

        # spread the passenger number to a time range
        def spread_function(row):
            trg = pd.date_range(row['aft'] - offset, periods=20, freq='Min')
            area = row['area']
            num = row['num']
            values = [[trg[idx], gen_num(idx, num), area] for idx in range(20)]
            return pd.DataFrame(values, columns=columns_name)

        for idx, row in self.sche.iterrows():
            tmp = tmp.append(spread_function(row))

        tmp = tmp.groupby([pd.Grouper(key='timeStamp', freq='1Min'), 'area']).sum()
        tmp = tmp.reset_index()
        tmp = tmp[
                (tmp['timeStamp'] >= self.date_start) & 
                (tmp['timeStamp'] <= self.date_end)
                ]

        return tmp

    def visualize_sum_output(self, gran=1):
        gran = str(gran) + 'Min'
        tmp = self.rst.groupby(pd.Grouper(key='timeStamp', freq=gran)).sum()
        tmp.plot()
        plt.show()

    def visualize_sum_output_for_each_area(self, gran=1):
        gran = str(gran) + 'Min'
        tmp = self.rst.groupby('area')

        for key in tmp.groups:
            foo = tmp.get_group(key)
            foo = foo.groupby(pd.Grouper(key='timeStamp', freq=gran)).sum()
            foo.plot()
            plt.title(key)
            plt.show()

if __name__ == '__main__':
    directory = './data1/'
    if len(sys.argv) >= 2 and os.path.exists(sys.argv[1]):
        directory = sys.argv[1]
    op = output_predict('2016/09/10 00:00:00', '2016/09/15 00:00:00', directory)
