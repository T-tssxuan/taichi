import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import GradientBoostingRegressor as gbdt
from sklearn.cross_validation import cross_val_score

class PredictDelay:
    '''
    Predict the delay time for a plane
    '''
    def __init__(self):
        self.csv = pd.read_csv('./data/airport_gz_flights_chusai_1stround.csv')
        del self.data['flight_ID']
        del self.data['BGATE_ID']
        self.data.columns = ['sch', 'act']

        data['act'] = pd.to_datetime(data['act'])
        data['sch'] = pd.to_datetime(data['sch'])

        data = data.sort_values('sch')
        data = data.reset_index()
        del data['index']
        
    def train(self):
        X, y = self.get_data()

        self.mean = y.mean()
        self.std = y.std()

        self.clf = gbdt(n_estimators=1000, max_depth=5, max_features='sqrt')
        rst = cross_val_score(self.clf, X, y)
        print(rst)
        info = 'result: ' + str(rst.mean()) + '% confidence and with ';
        info += str(rst.std()) + ' accuracy.'
        print(info)

        self.clf.fit(self.X, self.y)

    def predict(self, start, end):
        start = pd.to_datetime(start)
        end = pd.to_datetime(end)

        X, _ = get_predict_data(start, end)
        pdelay = self.clf.predict(X)

        return get_predict_result(start, end, pdelay)

    def get_predict_result(self, rstart, rend, rdelay):
        rdata = self.csv.copy()

        rdelay = rdelay.apply(lambda x: pd.DateOffset(minutes=x))

        offset = pd.DateOffset(sself.mean + 2.7 * self.std)
        rdata = rdata[rdata['sch'] > rstart - offset]
        rdata = rdata[rdata['sch'] < rend + offset]

        rdata['act'] = rdata['sch'].add(rdelay)

        rdata = rdata[rdata['act'] > rstart]

        return rdata['act']

    def get_predict_data(self, pstart, pend):
        pdata = self.csv.copy()

        offset = pd.DateOffset(sself.mean + 2.7 * self.std)
        pdata = pdata[pdata['sch'] > pstart - offset]
        pdata = pdata[pdata['sch'] < pend + offset]

        # get the random delay and then bind it the plane we need to predict
        ran_delay = np.random.normal(self.mean, self.std, len(pdata.shape[0]))
        ran_delay = pd.Series(ran_delay)
        pdata['act'] = pdata['sch'].add(ran_delay)
        return preprocess_data(data, offset)

    def get_train_data(self):
        tdata = self.csv.copy()
        return preprocess_data(tdata, 100)

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
        data['act'] = data['act'].add(pd.DateOffset(hours=8))
        data['act'] = data['act'].apply(func)
        data['sch'] = data['sch'].add(pd.DateOffset(hours=8))
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
