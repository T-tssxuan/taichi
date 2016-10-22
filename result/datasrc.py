import os
import time

class datasrc:
    info = ""
    data = "./data1/"
    ratio = '0.5'
    cur_time = time.strftime('%Y-%m-%d-%H-%M-%S')
    def get_info_dir():
        if datasrc.info == "":
            datasrc.info = './tmp/info-' + datasrc.cur_time + '/'
            os.mkdir(datasrc.info)
        return datasrc.info

    def get_data_dir():
        return datasrc.data

    def set_data_dir(dirname):
        datasrc.data = dirname

    def get_result_dir():
        s = 'info/result-' + datasrc.cur_time + '-' + str(datasrc.ratio) + '.csv'
        return s

    def get_wifi_ratio():
        return datasrc.ratio
