import numpy as np
import pandas as pd

class preProcesser:
    df = pd.DataFrame()
    def __init__(self,df):
        self.df = df
    def slice10(self,col_name,fmt):
        fs = self.df
        fs[col_name] = fs[col_name].str.slice(0,15).apply(lambda x:x+"0")
        fs[col_name] = pd.to_datetime(fs[col_name],format="%Y"+fmt[0]+"%m"+fmt[0]+"%d"+fmt[1]+"%H"+fmt[2]+"%M")
        return fs
    def str_2_date(self,col_name,fmt):
        fs = self.df
        fs[col_name] = pd.to_datetime(fs[col_name],format="%Y"+fmt[0]+"%m"+fmt[0]+"%d"+fmt[1]+"%H"+fmt[2]+"%M"+fmt[2]+"%S")
        return fs
    def get_week_day(self,col_name,week_name):
        fs = self.df
        fs[week_name] = fs[col_name].dt.weekday + 1
        return fs
    def get_day(self,col_name,day_name):
        fs = self.df
        fs[day_name] = fs[col_name].apply(lambda x:x.day)
        return fs
    def get_hour(self,col_name,hour_name):
        fs = self.df
        fs[hour_name] = fs[col_name].apply(lambda x:x.hour)
        return fs
    def minuteLevel(self,col_name,trans_name):
        fs =self.df
        fs[trans_name] = fs[col_name].apply(lambda x:x.replace(second=0))
        return fs
    def greenWich(self,col_name,trans_name):
        fs = self.df
        fs[trans_name] = fs[col_name].apply(lambda x:x+pd.DateOffset(hours=8))
        return fs
    def trim_space(self,col_name):
        fs = self.df
        fs[col_name] = fs[col_name].str.replace(" ","")
        return fs
    def get_area_small(self,col_name,area_name):
        fs = self.df
        fs[area_name] = fs[col_name].str.slice(0,2).apply(lambda x:x.upper())
        return fs
    def get_area_big(self,col_name,area_name):
        fs = self.df
        fs[area_name] = fs[col_name].str.slice(0,1).apply(lambda x:x.upper())
        return fs
    def get_company(self,col_name,company):
        fs = self.df
        fs[company] = fs[col_name].str.slice()

