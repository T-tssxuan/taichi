import os
import time

class datasrc:
    info = ""
    data = "./data1/"
    def get_info_dir():
        if datasrc.info == "":
            datasrc.info = 'info-' + time.strftime('%Y-%m-%d-%H-%M-%S')
            os.mkdir(datasrc.info)
        return datasrc.info

    def get_data_dir():
        return datasrc.data

    def set_data_dir(dirname):
        datasrc.data = dirname
