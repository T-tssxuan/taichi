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
        self.X, self.y = self.get_data()

    def train(self):
        params = {'n_estimators': 1000, 'max_depth': 5, 'max_feature': 'sqrt'}
        clf = gbdt(params)
        rst = cross_val_score(clf, self.X, self.y)
        print(rst)

    def get_data(self):
        data = pd.read_csv('./data/airport_gz_flights_chusai_1stround.csv')
        del data['flight_ID']
        del data['BGATE_ID']
        data.columns = ['sch', 'act']

        data = data[pd.notnull(data['act'])]
        data['act'] = pd.to_datetime(data['act'])

        data = data[pd.notnull(data['sch'])]
        data['sch'] = pd.to_datetime(data['sch'])
        
        data = data.sort_values('sch')

        data = data.reset_index()
        del data['index']

        # func1 = lambda x: data[data['sch'] >= x['sch']][data['sch'] <= x['act']]
        # data['sch_overlap'] = data['sch'].apply(func1)

        sch_overlap = {}
        for idx, row in data.iterrows():
            tmp = data[data['sch'] >= row['sch']]
            tmp = tmp[tmp['sch'] <= row['act']]
            sch_overlap[idx] = tmp.shape[0]
        sch_overlap = pd.DataFrame.from_dict(sch_overlap, 'index')
        sch_overlap.columns = ['sch_overlap']
        
        # func1 = lambda x: data[data['act'] >= x['sch']][data['act'] <= x['act']]
        # data['act_overlap'] = data['sch'].apply(func1)

        act_overlap = {}
        for idx, row in data.iterrows():
            tmp = data[data['act'] >= row['sch']]
            tmp = tmp[tmp['act'] <= row['act']]
            act_overlap[idx] = tmp.shape[0]
        act_overlap = pd.DataFrame.from_dict(act_overlap, 'index')
        act_overlap.columns = ['act_overlap']

        data = pd.concat([data, sch_overlap], axis=1)
        data = pd.concat([data, act_overlap], axis=1)

        func = lambda x: x.total_seconds()
        data['delay'] = data['act'].subtract(data['sch']).apply(func)
        data = data[data['delay'] < 400]
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
