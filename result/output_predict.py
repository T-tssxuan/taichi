import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

class output_predict:
    '''
    attributes:
        sche: the plane schedule information
        output_predict: the output predict for each area
        gate: teh airport gate and area relationship table
        distribute: the area scheduled plane distribute
        empty_count: the number of plane which is not given setting off area 
        passenger: the passenger number of each plane table
        date_start: the start of the predict day
        date_end: the end of the predict day 
    '''
    def __init__(self, directory):
        self.directory = directory
        path = self.directory + 'airport_gz_flights_chusai.csv'

        self.sche = pd.read_csv(path)
        self.sche.columns = ['fid', 'sft', 'aft', 'gate']
        self.sche['sft'] = pd.to_datetime(self.sche['sft'])
        self.sche['aft'] = pd.to_datetime(self.sche['aft'])
        self.sche['fid'] = self.sche['fid'].str.upper()
        self.sche['fid'] = self.sche['fid'].str.replace(' ', '')
        self.sche['gate'] = self.sche['gate'].str.replace(' ', '')

        self.__fill_delay_for_without_actual_flt()
        self.__fill_area_according_to_gate()
        self.__fill_passenger_number_according_statistic()

        del self.sche['sft']
        del self.sche['gate']
        del self.sche['fid']

        self.__get_output_predict_for_each_area()
        self.output_predict.to_csv(
                './info/output_predict.csv', 
                columns=['timeStamp', 'num', 'area'],
                index=False
                )

    def __get_output_date_range(self):
        min_time = self.sche['sft'].min()
        self.date_start = str(min_time.year) + '/' + str(min_time.month) + '/'
        self.date_start += str(min_time.day)

        max_time = self.sche['sft'].max()
        max_time += pd.DateOffset(days=1)
        self.date_end = str(max_time.year) + '/' + str(max_time.month) + '/'
        self.data_end += str(max_time.day)

    def __fill_delay_for_without_actual_flt(self):
        print('fill delay for without actual flight time')
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
        print('fill area according to the flight gate')
        self.gate = pd.read_csv(self.directory + './airport_gz_gates.csv')
        self.gate.columns = ['gate', 'area']
        self.gate['gate'] = self.gate['gate'].str.replace(' ', '')
        self.gate['area'] = self.gate['area'].str.replace(' ', '')
        self.gate = self.gate.set_index('gate')

        tmp = ['W1', 'W2', 'W3', 'E1', 'E2', 'E3']
        # record the number gate without area
        self.empty_count = 0
        # count each area scheduled plane number
        self.distribute = {'W1': 0, 'W2': 0, 'W3': 0, 'E1': 0, 'E2': 0, 'E3': 0}
        def func(x):
            if x in self.gate.index:
                self.distribute[self.gate.loc[x, 'area']] += 1
                return self.gate.loc[x, 'area']
            else:
                self.empty_count += 1
                return tmp[np.random.randint(6)]
        self.sche['area'] = self.sche['gate'].apply(func)


    def __fill_passenger_number_according_statistic(self):
        print('fill passenger number according statistic')
        self.passenger = pd.read_csv('./info/flight_passenger_num.csv')
        self.passenger.columns = ['fid', 'num']
        self.passenger['fid'] = self.passenger['fid'].str.replace(' ', '')
        self.passenger = self.passenger.set_index('fid')

        # get the mean and the std of the flight passenger num to fill the blank
        std = self.passenger.std()
        mean = self.passenger.mean()

        self.sum_flight = 0
        self.miss_passenger = 0
        self.miss_fid = []
        def get_number(x):
            self.sum_flight += 1
            if x in self.passenger.index:
                return self.passenger.loc[x, 'num']
            else:
                self.miss_fid.append(x)
                self.miss_passenger += 1
                # fill the empty data with the mean and std
                tmp = std * np.random.randn() + mean
                # tmp = 0
                if tmp < 0:
                    tmp = 1
                elif tmp > 300:
                    tmp = 300
                return tmp
        self.sche['num'] = self.sche['fid'].apply(get_number)

    def __get_output_predict_for_each_area(self):
        print('get output predict for each plane')

        columns_name = ['timeStamp', 'num', 'area']

        offset = pd.DateOffset(minutes=20)

        # generate output info for each minutes in the given time range
        rgn = pd.date_range(self.date_start, self.date_end, freq='Min')
        areas = ['W1', 'W2', 'W3', 'E1', 'E2', 'E3']
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
        self.output_predict = tmp.reset_index()

    def visualize_sum_output(self, gran=1):
        gran = str(gran) + 'Min'
        tmp = self.output_predict.groupby(pd.Grouper(key='timeStamp', freq=gran)).sum()
        tmp.plot()
        plt.show()

    def visualize_sum_output_for_each_area(self, gran=1):
        gran = str(gran) + 'Min'
        tmp = self.output_predict.groupby('area')

        for key in tmp.groups:
            foo = tmp.get_group(key)
            foo = foo.groupby(pd.Grouper(key='timeStamp', freq=gran)).sum()
            foo.plot()
            plt.title(key)
            plt.show()
