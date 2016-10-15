import ap_user
import pandas as pd

class main:
    def get_result(self, start, end, gran):
        return ap_user.get_range_data(start, end, gran)
