import pandas as pd
import numpy as np
from ap_user_predict_data import ap_user_predict_data

data_source = ap_user_predict_data()

class ap_user:
    def __init__(self, gran):
        '''
        params:
            gran: the granurality of the result
        attributes:
            gran: the granurality of the result
            in_data: the input data
            out_data: the output data
            base_data: the initial ap user number
            ap_ratio_data: the ap ratio in it's area
        '''
        self.gran = gran
        self.in_data = data_source.get_in_data()
        self.out_data = data_source.get_out_data()
        self.base_data = data_source.get_base_data()
        self.ap_ratio_data = data_source.get_ap_ratio_data()

    def __generate_predict(self):
        # the result colums name
        tmp = 'slice' + str(self.gran) + 'min'
        columns = ['passengerCount', 'WIFIAPTag', tmp, 'area']

        # calculate the pure input of each area
        self.in_data = self.in_data.set_index(['timeStamp', 'area'])
        self.out_data = self.out_data.set_index(['timeStamp', 'area'])

        net_in = self.in_data.subtract(self.out_data)
        net_in = net_in.reset_index()

        # gruop pure input by each area
        net_in = net_in.groupby('area')

        # set the base passenger for each ap
        base_num = self.base_data.set_index(['area', 'WIFIAPTag'])

        # init the ratio info for each ap
        ratio_data = self.ap_ratio_data.set_index(['area', 'WIFIAPTag'])

        # initial the result
        result = pd.DataFrame([], columns=columns)

        # datetime transform to the final format
        def date_func(x): 
            s = str(x.year) + '-' + str(x.month) + '-'
            s += str(x.day) + '-' + str(x.hour) + '-' + str(x.minute)
            return s

        # generate the result for each area and each ap of the area
        for area in net_in.keys():
            # preprocess the pure input of the area
            sec_net_in = net_in.get_group(area)
            del sec_net_in['area']
            sec_net_in = sec_net_in.set_index(['timeStamp'])
            sec_net_in = sec_net_in.sort_index()
            sec_net_in = sec_net_in.cumsum(axis=0)
            sec_net_in = sec_net_in.reset_index()

            # current_num = base_num + acc_num * ratio_of_area
            for ap_area, ap_tag in base_num.index:
                if ap_area != area:
                    continue

                # get the ratio and bas
                ratio = ratio_data.loc[(ap_area, ap_tag), 'ratio']
                num = base_num.loc[(ap_area, ap_tag), 'passengerCount']

                func = lambda x: x * ratio + num
                
                # get this area and aptag data
                rst = pd.DataFrame(
                        np.array([
                            [sec_net_in['passengerCount'].apply(func).values],
                            [ap_tag for i in len(sec_net_in.index)],
                            [sec_net_in['timeStamp'].values]
                            ]).transpose(),
                        columns=columns
                        )
                result = result.append(rst)

        # set the granularity to the self.gran
        result = result.groupby(
                ['WIFIAPTag', pd.Grouper(key='slice10min', freq=str(self.gran) + 'Min')]
                ).sum()
        result = result.reset_index()
        result = result[columns]

        return result

