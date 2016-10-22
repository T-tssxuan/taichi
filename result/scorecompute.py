import numpy as np
import pandas as pd
from preprocess import preProcesser

class scoreCompute:
    path_wifi = ""
    path_res = ""
    test_day = 0
    test_time_low = ""
    test_time_high = ""
    def __init__(self,pw,pr,td,tl,th):
        self.path_wifi = pw
        self.path_res = pr
        self.test_day = td
        self.test_time_low = tl
        self.test_time_high = th
    def initial(self):
        wifi = pd.read_csv(self.path_wifi)
        wp = preProcesser(wifi)
        wifi = wp.trim_space("WIFIAPTag")
        wifi = wp.slice10("timeStamp",["-","-","-"])
        wifi = wp.get_day("timeStamp","day")
        wifi = wp.get_week_day("timeStamp","week_day")
        wifi1 = wifi.loc[wifi.day>11]
        wifi1 = wifi[["WIFIAPTag","timeStamp","passengerCount"]]
        wifi1 = wifi1.groupby(["WIFIAPTag","timeStamp"],as_index=False).sum()
        wp1 = preProcesser(wifi1)
        wifi1 = wp1.get_day("timeStamp","day")
        wifi1 = wp1.get_week_day("timeStamp","week_day")
        wifi1["timeStamp"] = wifi1["timeStamp"].apply(lambda x:x.strftime('%Y-%m-%d %H:%M:%S'))
        wifi1["timeStamp"] = wifi1["timeStamp"].str.slice(11,16)
        return wifi1
    def get_score(self,wifi1):
        test = wifi1.loc[wifi1.day==self.test_day]
        train = wifi1.loc[wifi1.day!=self.test_day]
        weekDay = int(test["week_day"].unique())
        #if weekDay==7:
        #    train_week = wifi1.loc[(wifi1.week_day==6)|(wifi1.week_day==7)]
        #else:
        train_week = wifi1.loc[wifi1.week_day==weekDay]
        wifi2 = train[["WIFIAPTag","timeStamp","passengerCount"]]
        wifi2 = wifi2.groupby(["WIFIAPTag","timeStamp"],as_index=False).median()

        wifi3 = train_week[["WIFIAPTag","timeStamp","passengerCount"]]
        wifi3 = wifi3.groupby(["WIFIAPTag","timeStamp"],as_index=False).median()
        wifi3.columns = ["WIFIAPTag","timeStamp","p3"]
        wifi2 = pd.merge(wifi2,wifi3,how="inner",on=["WIFIAPTag","timeStamp"])
        #if weekDay==7:
        wifi2["p2"] = 0.4*wifi2["passengerCount"] + 0.6*wifi2["p3"]
        #else:
            #wifi2["p2"] = (wifi2["passengerCount"] + wifi2["p3"])/2.0
        wifi2 = wifi2[["WIFIAPTag","timeStamp","p2"]]
        wifi2.columns = ["WIFIAPTag","timeStamp","passengerCount"]
        test_period = test.loc[(test.timeStamp>=self.test_time_low)&(test.timeStamp<=self.test_time_high)]
        test_period = test_period[["WIFIAPTag","timeStamp","passengerCount"]]
        test_period.columns = ["WIFIAPTag","timeStamp","ptest"]
        test_period["ptest"] = (test_period["ptest"].apply(lambda x:float(x)))/10.0
        tag = pd.Series(test.loc[test.timeStamp<self.test_time_low,"WIFIAPTag"].unique())
        test_period = test_period.set_index("WIFIAPTag")
        test_period = test_period.loc[tag]
        test_period = test_period.reset_index()
        res = pd.read_csv(self.path_res)
        res = res[["WIFIAPTag","slice10min","passengerCount"]]
        res.columns = ["WIFIAPTag","timeStamp","ptrain"]
        res["timeStamp"] = res["timeStamp"].str.slice(10)
        res["timeStamp"] = res["timeStamp"].str.replace("-",":")
        res["timeStamp"] = res["timeStamp"].apply(lambda x:x+"0")
        score = pd.merge(test_period,res,how="inner",on=["WIFIAPTag","timeStamp"])
        #score = pd.merge(test_period,wifi2_period,how="inner",on=["WIFIAPTag","timeStamp"])
        #score = pd.merge(test_period,wifi2_period,how="outer",on=["WIFIAPTag","timeStamp"])
        score.fillna(0)
        score["diff"] = score["ptrain"]-score["ptest"]
        score["square_diff"] = score["diff"].apply(lambda x:x*x)
        s = score["square_diff"].sum()
        return s,score
