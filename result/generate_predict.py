import pandas as pd
import numpy as np
from generate_base_data import generate_base_data
from log import debug
from datasrc import datasrc
import time

def generate_predict(start, end, gran=10):
    info_dir = datasrc.get_info_dir()

    debug('start: ' + str(start) + ' end: ' + str(end) + ' gran' + str(gran))
    start = pd.to_datetime(start)
    end = pd.to_datetime(end)

    # the result colums name
    slice_column = 'slice' + str(gran) + 'min'
    columns = ['passengerCount', 'WIFIAPTag', slice_column]

    # get the base data
    base_data = pd.read_csv(info_dir + 'base_data.csv')

    # get the net in data
    net_in = pd.read_csv(info_dir + 'variation_data.csv')
    net_in['timeStamp'] = pd.to_datetime(net_in['timeStamp'])
    net_in = net_in.groupby(
            ['area', pd.Grouper(key='timeStamp', freq='1Min')]
            ).sum()
    net_in = net_in.reset_index()

    net_in = net_in[
            (net_in['timeStamp'] >= start) &
            (net_in['timeStamp'] < end)
            ]

    net_in = net_in.groupby('area')

    # set the base passenger for each ap
    base_data = base_data.set_index(['area', 'WIFIAPTag'])

    # initial the result
    result = pd.DataFrame([], columns=columns)

    # datetime transform to the final format
    def date_func(x): 
        s = str(x.year) + '-' + str(x.month) + '-'
        s += str(x.day) + '-' + str(x.hour) + '-' + str(int(x.minute / 10))
        return s

    # generate the result for each area and each ap of the area
    for area in net_in.groups:
        # preprocess the pure input of the area
        sec_net_in = net_in.get_group(area).copy()
        del sec_net_in['area']
        sec_net_in = sec_net_in.set_index('timeStamp')
        sec_net_in = sec_net_in.sort_index()
        sec_net_in = sec_net_in.cumsum(axis=0)
        sec_net_in = sec_net_in.reset_index()

        # current_num = base_data + acc_num * ratio_of_area
        for ap_area, ap_tag in base_data.index:
            if ap_area != area:
                continue

            # get the ratio and bas
            ratio = base_data.loc[(ap_area, ap_tag), 'ratio']
            num = base_data.loc[(ap_area, ap_tag), 'passengerCount']

            func = lambda x: x * ratio + num
            
            # get this area and aptag data
            rst = pd.DataFrame(
                    np.array([
                        sec_net_in['num'].apply(func).values,
                        [ap_tag for i in range(sec_net_in.shape[0])],
                        sec_net_in['timeStamp'].values
                        ]).transpose(),
                    columns=columns
                    )
            result = result.append(rst)

    debug("\n" + str(result.head()) + "\n")
    result['slice10min'] = pd.to_datetime(result['slice10min'])
    # set the granularity to the gran
    result = result.groupby(
            ['WIFIAPTag', pd.Grouper(key=slice_column, freq=str(gran) + 'Min')]
            ).sum()
    result = result.reset_index()
    result[slice_column] = result[slice_column].apply(date_func)
    result['passengerCount'] = result['passengerCount'] / 10
    result = result[columns]

    file_name = datasrc.get_result_dir()
    result.to_csv(file_name, columns=columns, index=False)
    return result


if __name__ == '__main__':
    start = '2016/09/14 15:00:00'
    end = '2016/09/14 18:00:00'
    aup = generate_predict(start, end)
    # ap_user_predict.generate_predict()
