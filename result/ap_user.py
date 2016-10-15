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
            ap_ratio_data: the ap ratio in it's section
        '''
        self.gran = gran
        self.in_data = data_source.get_in_data(gran)
        self.out_data = data_source.get_out_data(gran)
        self.base_data = data_source.get_base_data(gran)
        self.ap_ratio_data = data_source.get_ap_ratio_data()


    def __generate_predict(self):
        # the result colums name
        tmp = 'slice' + str(self.gran) + 'min'
        columns = ['passengerCount', 'WIFIAPTag', tmp, 'section']

        # calculate the pure input of each section
        self.in_data = self.in_data.set_index(['timeStamp', 'section'])
        self.out_data = self.out_data.set_index(['timeStamp', 'section'])

        net_in = self.in_data.subtract(self.out_data)
        net_in = net_in.reset_index()

        # gruop pure input by each section
        net_in = net_in.groupby('section')

        # set the base passenger for each ap
        base_num = self.base_data.set_index(['section', 'WIFIAPTag'])

        # init the ratio info for each ap
        ratio_data = self.ap_ratio_data.set_index(['section', 'WIFIAPTag'])

        # initial the result
        result = pd.DataFrame([], columns=columns)

        # datetime transform to the final format
        def date_func(x): 
            s = str(x.year) + '-' + str(x.month) + '-'
            s += str(x.day) + '-' + str(x.hour) + '-' + str(x.minute)
            return s

        # generate the result for each section and each ap of the section
        for section in net_in.keys():
            # preprocess the pure input of the section
            sec_net_in = net_in.get_group(section)
            del sec_net_in['section']
            sec_net_in = sec_net_in.set_index(['timeStamp'])
            sec_net_in = sec_net_in.sort_index()
            sec_net_in = sec_net_in.cumsum(axis=0)
            sec_net_in = sec_net_in.reset_index()

            # current_num = base_num + acc_num * ratio_of_section
            for ap_section, ap_tag in base_num.index:
                if ap_section != section:
                    continue

                # get the ratio and bas
                ratio = ratio_data.loc[(ap_section, ap_tag), 'ratio']
                num = base_num.loc[(ap_section, ap_tag), 'passengerCount']

                func = lambda x: x * ratio + num
                
                # get this section and aptag data
                rst = pd.DataFrame(
                        np.array([
                            [sec_net_in['passengerCount'].apply(func).values],
                            [ap_tag for i in len(sec_net_in.index)],
                            [sec_net_in['timeStamp'].apply(date_func).values]
                            ]).transpose(),
                        columns=columns
                        )
                result = result.append(rst)

        return result

