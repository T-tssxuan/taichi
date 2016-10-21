import sys
import pandas as pd
import numpy as np
from ap_user_predict import ap_user_predict
from generate_ap_ratio_info import  generate_ap_ratio_info
from generate_base_data import generate_base_data
from generate_flight_passenger import generate_flight_passenger
from generate_pure_variation import generate_pure_variation
from output_predict import output_predict
from input_predict import input_predict
from log import log


if __name__ == '__main__':
    directory = './data1/'
    start = '2016-09-25-15-00-00'
    end = '2016-09-25-18-00-00'
    fmt = '%Y-%m-%d-%H-%M-%S'

    range_start = '2016/09/10 00:00:00'
    range_end = '2016/09/15 00:00:00'

    # get the dirtory of source data need to predicting
    if len(sys.argv) >= 2:
        directory = sys.argv[1]

    # get the prediction range 
    if len(sys.argv) >= 4:
        if pd.notnull(pd.to_datetime(sys.argv[2], format=fmt)) \
                and pd.notnull(pd.to_datetime(sys.argv[3], format=fmt)):
            start = sys.argv[2]
            end = sys.argv[3]
        else:
            print('Please input time in the form: YYYY-MM-DD-HH-MM-SS')

    start = pd.to_datetime(start, format=fmt)
    end = pd.to_datetime(end, format=fmt)

    # # generate the pasenger number stastistic info for each flight id
    # log('generate the passenger number')
    # generate_flight_passenger(directory)
    #
    # # generate each ap user ratio in their area
    # log('generate ap ratio info')
    # generate_ap_ratio_info(directory)
    #
    # # generate airport output predict for each area
    # log('genrate output predict for each area')
    # op = output_predict(range_start, range_end, directory)
    #
    # # generate airport checkin input predict for each area
    # log('generate checkin predict')
    # cip = input_predict(0, directory)
    # cip.train(range_start, range_end)
    #
    # # generate airport security predict for each area
    # log('generate security predict')
    # sip = input_predict(1, directory)
    # sip.train(range_start, range_end)
    #
    # # generate purely variation for each area
    # log('generate pure variation predict')
    # generate_pure_variation()
    #
    # # generate the base data for prediction
    # log('generate the base data')
    # generate_base_data(directory, '2016/09/14 14:59:00')

    log('predict the result')
    ap_user_predict = ap_user_predict('', '')
    ap_user_predict.generate_predict('', '')

    log('finish')
