import sys
import pandas as pd
import numpy as np
from ap_user_predict import ap_user_predict
from generate_ap_ratio_info import  generate_ap_ratio_info
from generate_base_data import generate_base_data
from generate_flight_passenger_number import generate_flight_passenger_number
from output_predict import output_predict

if __main__ == '__main__':
    directory = './data1/'
    prediction_start = '2016-09-25-15-00-00'
    prediction_end = '2016-09-25-18-00-00'
    fmt = '%Y-%m-%d-%H-%M-%S'

    # get the dirtory of source data need to predicting
    if len(sys.argv) >= 2:
        directory = sys.argv[1]

    # get the prediction range 
    if len(sys.argv) >= 4:
        if pd.notnull(pd.to_datetime(sys.argv[2], format=fmt)) \
                and pd.notnull(pd.to_datetime(sys.argv[3], format=fmt)):
            prediction_start = sys.argv[2]
            prediction_end = sys.argv[3]
        else:
            print('Please input time in the form: YYYY-MM-DD-HH-MM-SS')

    prediction_start = pd.to_datetime(prediction_start, format=fmt)
    prediction_end = pd.to_datetime(prediction_end, format=fmt)

    # generate the pasenger number stastistic info for each flight id
    generate_flight_passenger_number(directory)
    # generate airport output predict for each area
    output_predict = output_predict(directory, p_num_std, p_num_mean)

    # generate each ap user ratio in their area
    generate_ap_ratio_info(directory)
    # generate the base data for prediction
    generate_base_data(directory, prediction_start)

    ap_user_predict = ap_user_predict()
    ap_user_predict.generate_predict()
