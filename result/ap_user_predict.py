import pandas as pd
import numpy as np
from generate_base_data import generate_base_data
from log import debug

def generate_predict(directory, start, end, gran=10):
    debug('start: ' + str(start) + ' end: ' + str(end) + ' gran' + str(gran))
    start = pb.to_datetime(start)
    end = pb.to_datetime(end)

    # the result colums name
    slice_column = 'slice' + str(gran) + 'min'
    columns = ['passengerCount', 'WIFIAPTag', slice_column]

    # generate the base data
    base_data = generate_base_data(directory, start)

    net_in = pd.read_csv('./info/variation_data.csv')
    net_in['timeStamp'] = pd.to_datetime(net_in['timeStamp'])
    net_in = net_in.groupby(
            ['area', pd.Grouper(key='timeStamp', freq=gran)]
            ).sum()
    net_in = net_in.reset_index()

    net_in = net_in[
            (net_in['timeStamp'] >= start) &
            (net_in['timeStamp'] <= end)
            ]

    net_in = net_in.groupby('area')

    # set the base passenger for each ap
    base_data = base_data.set_index(['area', 'WIFIAPTag'])

    # initial the result
    result = pd.DataFrame([], columns=columns)

    # datetime transform to the final format
    def date_func(x): 
        s = str(x.year) + '-' + str(x.month) + '-'
        s += str(x.day) + '-' + str(x.hour) + '-' + str(x.minute)
        return s

    # generate the result for each area and each ap of the area
    for area in net_in.groups:
        # preprocess the pure input of the area
        sec_net_in = net_in.get_group(area)
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
            ['WIFIAPTag', pd.Grouper(key='slice10min', freq=str(gran) + 'Min')]
            ).sum()
    result = result.reset_index()
    result = result[columns]

    result.to_csv('./info/result.csv', columns=columns, index=False)
    return result


if __name__ == '__main__':
    directory = './data1/'
    start = '2016/09/14 15:00:00'
    end = '2016/09/14 18:00:00'
    aup = generate_predict(directory, start, end)
    # ap_user_predict.generate_predict()
