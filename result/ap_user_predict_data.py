import pandas as pd

'''
This module is provide data to the ap_user data, there are three types of data,
the total input data, the total output data, the current total user data, the 
ratio of each ap in their area.
The table detail is as follow:

input data: dictionary, each area is a key include: W1, W2, W3, E1, E2...
and each entry table:
    -------------------------------------------
         timeStamp       |    num    |  area
    --------------------------------------------
     2016-09-14 12:30:00 |     3     |   W1
    --------------------------------------------
           ....          |     x     |   W2
    --------------------------------------------
                ..........

output data: dictionary, each area is a key include: W1, W2, W3, E1, E2...
and each entry table:
    -------------------------------------------
         timeStamp       |    num    |  area
    --------------------------------------------
     2016-09-14 12:30:00 |     3     |   W1
    --------------------------------------------
           ....          |     x     |   W2
    --------------------------------------------
                       ..........

base_data: dictionary, each area is a key included: W1, W2, W3, E1, E2....
   area       WIFIAPTag         passengerCount   
     W1         E1-1A-1<E1-1-01>        15          
     W1         E1-1A-2<E1-1-02>        15          
     W1         E1-1A-3<E1-1-03>        38          
     W1         E1-1A-4<E1-1-04>        19          
     W1         E1-1A-5<E1-1-05>         0          

ap_ratio_data: dictionary, each area key included: W1, W2, W3, E1, E2...
    area         WIFIAPTag             ratio
      W1           E1-1A-1<E1-1-01>        x1
      W1           E1-1A-2<E1-1-02>        x2 
      W1           E1-1A-3<E1-1-03>        x3
      W1           E1-1A-4<E1-1-04>        x4   
      W1           E1-1A-5<E1-1-05>        x5 

'''

class ap_user_predict_data:
    def __init__(self):
        self.__init_in_data()
        self.__init_out_data()
        self.__init_base_data()
        self.__init_ap_ratio_data()

    def __init_in_data(self):
        # alert for the error Ec
        self.in_data = pd.read_csv('./info/input_data.csv')
        self.in_data['timeStamp'] = pd.to_datetime(self.in_data['timeStamp'])

    def __init_out_data(self):
        self.out_data = pd.read_csv('./info/output_data.csv')
        self.out_data['timeStamp'] = pd.to_datetime(self.out_data['timeStamp'])

    def __init_base_data(self):
        self.base_data = pd.read_csv('./info/base_data.csv')

    def __init_ap_ratio_data(self):
        self.ap_ratio_data = pd.read_csv('./info/ap_ratio_data.csv')

    # return data by the granularity
    def get_in_data(self, gran=1):
        tmp = self.in_data.copy()
        tmp = tmp.groupby(['area', pd.TimeGrouper(gran)]).sum()
        tmp = tmp.reset_index()
        return tmp

    # return data by the granularity
    def get_out_data(self, gran=1):
        tmp = self.out_data.copy()
        tmp = tmp.groupby(pd.TimeGrouper(gran)).sum()
        tmp = tmp.reset_index()
        return tmp

    # return data by the granularity
    def get_base_data(self, gran=1):
        tmp = self.base_data.copy()
        tmp = tmp.reset_index()
        return tmp

    def get_ap_ratio_data(self):
        tmp = self.ap_ratio_data.copy()
        return tmp
