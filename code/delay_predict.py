import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import GradientBoostingRegressor as gbdt
from sklearn.cross_validation import cross_val_score
from sklearn.metrics import mean_squared_error 

class PredictDelay:
    '''
    Predict the delay time for a plane
    '''
    def __init__(self):
        self.csv = pd.read_csv('./data/airport_gz_flights_chusai_1stround.csv')
        del self.csv['flight_ID']
        del self.csv['BGATE_ID']
        self.csv.columns = ['sch', 'act']

        self.csv['act'] = pd.to_datetime(self.csv['act'])
        self.csv['sch'] = pd.to_datetime(self.csv['sch'])

        self.csv['sch'] = self.csv['sch'].add(pd.DateOffset(hours=8))
        self.csv['act'] = self.csv['act'].add(pd.DateOffset(hours=8))

        self.csv = self.csv.sort_values('sch')
        self.csv = self.csv.reset_index()
        del self.csv['index']
        
        self.csv.info()
        

    def predict(self, start, end):
        start = pd.to_datetime(start)
        end = pd.to_datetime(end)

        X, _ = self.get_predict_data(start, end)
        X.info()

        pdelay = self.clf.predict(X)

        self.validate_predict_result(start, end, pdelay)

        return self.get_predict_result(start, end, pdelay)

    def get_predict_result(self, rstart, rend, rdelay):
        rdata = self.csv.copy()

        offset = pd.DateOffset(minutes=self.mean + 2.7 * self.std)
        rdata = rdata[rdata['sch'] > rstart - offset]
        rdata = rdata[rdata['sch'] < rend + offset]

        rdata = rdata.reset_index()
        del rdata['index']

        func = lambda x: pd.Timedelta(x, unit='m')
        rdelay = pd.Series(rdelay).apply(func)
        rdata['act'] = rdata['sch'].add(rdelay)

        rdata = rdata[rdata['act'] > rstart]

        return rdata['act']

    def validate_predict_result(self, rstart, rend, rdelay):
        rdata = self.csv.copy()

        confident = int(self.mean + 2.7 * self.std)
        offset = pd.DateOffset(minutes=confident)
        rdata = rdata[rdata['sch'] > rstart - offset]
        rdata = rdata[rdata['sch'] < rend + offset]

        # rdata = rdata.reset_index()
        # del rdata['index']
        # rdata = rdata[rdata['sch'] > rstart]

        # func = lambda x: pd.Timedelta(x, unit='m')
        # rdelay = pd.Series(rdelay).apply(func)
        # rst = rdata['sch'].add(rdelay)
        # rst = rst[rst > rstart]

        func = lambda x: x.total_seconds() / 60
        tdelay = rdata['act'].subtract(rdata['sch'])
        tdelay = tdelay.apply(func)
        tdelay = tdelay.fillna(22)

        self.td = tdelay
        self.rd = rdelay

        val = mean_squared_error(rdelay, tdelay)

        print('validate result: ' + str(val))

    def get_predict_data(self, pstart, pend):
        pdata = self.csv.copy()

        confident = int(self.mean + 2.7 * self.std)
        offset = pd.DateOffset(minutes=confident)

        pdata = pdata[pdata['sch'] > pstart - offset]
        pdata = pdata[pdata['sch'] < pend + offset]

        pdata = pdata.reset_index()
        del pdata['index']

        # get the random delay and then bind it the plane we need to predict
        ran_delay = np.random.normal(self.mean, self.std, pdata.shape[0])
        func = lambda x: pd.Timedelta(x, unit='m')
        ran_delay = pd.Series(ran_delay).apply(func)
        pdata['act'] = pdata['sch'].add(ran_delay)
        
        self.tt = ran_delay
        self.pdata = pdata
        return self.preprocess_data(pdata, confident)

    def train(self):
        X, y = self.get_train_data()

        self.mean = y.mean()
        self.std = y.std()

        self.clf = gbdt(n_estimators=1000, max_depth=5, max_features='sqrt')
        rst = cross_val_score(self.clf, X, y)
        data['sch'] = data['sch'].add(pd.DateOffset(hours=8))
        print(rst)
        info = 'result: ' + str(rst.mean()) + '% confidence and with +/-';
        info += str(rst.std()) + ' accuracy.'
        print(info)

        self.clf.fit(X, y)

    def get_train_data(self):
        tdata = self.csv.copy()
        return self.preprocess_data(tdata, 100)

    def preprocess_data(self, data, delay_treshold):
        data = data[pd.notnull(data['act'])]
        data = data[pd.notnull(data['sch'])]
        
        sch_overlap = {}
        for idx, row in data.iterrows():
            tmp = data[data['sch'] >= row['sch']]
            tmp = tmp[tmp['sch'] <= row['act']]
            sch_overlap[idx] = tmp.shape[0]
        sch_overlap = pd.DataFrame.from_dict(sch_overlap, 'index')
        sch_overlap.columns = ['sch_overlap']
        
        act_overlap = {}
        for idx, row in data.iterrows():
            tmp = data[data['act'] >= row['sch']]
            tmp = tmp[tmp['act'] <= row['act']]
            act_overlap[idx] = tmp.shape[0]
        act_overlap = pd.DataFrame.from_dict(act_overlap, 'index')
        act_overlap.columns = ['act_overlap']

        data = pd.concat([data, sch_overlap], axis=1)
        data = pd.concat([data, act_overlap], axis=1)

        func = lambda x: x.total_seconds() / 60
        data['delay'] = data['act'].subtract(data['sch']).apply(func)
        data = data[data['delay'] < delay_treshold]
        delay = data['delay']
        del data['delay']

        func = lambda x: x.hour + x.minute / 60
        data['act'] = data['act'].apply(func)
        data['sch'] = data['sch'].apply(func)
        
        return (data, delay)


# params = {'n_estimators': 1000, 'max_depth': 5, 'max_feature': 'sqrt'}
# clf = gbdt(n_estimators=1000, max_depth=5, max_features='sqrt')
# rst = cross_val_score(clf, x, y)
# print(rst)


# from sklearn.metrics import mean_squared_error 
# params = {'n_estimators': 1000, 'max_depth': 5, 'max_feature': 'sqrt'}
# clf = gbdt(n_estimators=1000, max_depth=5, max_features='sqrt')
# offset = int(x.shape[0] * 0.1)
# X_train, y_train = x[:offset], y[:offset]
# X_test, y_test = x[offset:], y[offset:]
# clf.fit(X_train, y_train)
# rst = mean_squared_error(y_test, clf.predict(X_test))
# print(rst)
