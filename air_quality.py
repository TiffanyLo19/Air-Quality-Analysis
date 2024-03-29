# -*- coding: utf-8 -*-
"""Air Quality.ipynb
# Libraries and Data Loading
"""

!pip install scikit-plot
!pip install sklearn-evaluation

# Import files and libraries
import pandas as pd
import numpy as np
import sklearn
import seaborn as sns
import urllib.request as urllib2
import warnings
import matplotlib.pyplot as plt
import xgboost as xgb
import multiprocessing
import datetime
import graphviz
import scikitplot as skplt
import matplotlib.pyplot as plt
import statsmodels.api as sm
from statsmodels.sandbox.regression.predstd import wls_prediction_std
from sklearn.model_selection import train_test_split
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, precision_score, confusion_matrix, mean_squared_error, mean_absolute_error, r2_score, explained_variance_score
from sklearn.linear_model import LinearRegression
from datetime import datetime
from sklearn.metrics import mean_squared_error, mean_absolute_error
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn_evaluation import plot
from sklearn.metrics import accuracy_score, classification_report
from sklearn import tree
import graphviz
from sklearn import metrics
from sklearn.metrics import r2_score
from sklearn.tree import export_graphviz
from sklearn.linear_model import SGDRegressor
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier, RandomForestRegressor, AdaBoostRegressor
from sklearn.tree import DecisionTreeClassifier
from sklearn import preprocessing
from sklearn import utils
from sklearn.tree import DecisionTreeRegressor
from zipfile import ZipFile
from io import BytesIO

# Supress warnings
warnings.filterwarnings("ignore")

# Obtain and load data
url = urllib2.urlopen("https://archive.ics.uci.edu/ml/machine-learning-databases/00360/AirQualityUCI.zip").read()
files = ZipFile(BytesIO(url))

filenames = files.namelist()

myCSV = files.open(filenames[1])

# Create DF
data = pd.read_excel(myCSV, na_values = '-200.0')

"""# Data Exploration and Cleaning"""

data.describe()

data.dtypes # Check datatypes

# Merge date and time column
data['DateTime'] = data['Date'].astype(str) + ' ' + data['Time'].astype(str)
data1 = data.drop(['Date', 'Time'], axis = 1)

# Convert datatypes to strings for merge
data1['DateTime'] = pd.to_datetime(data1['DateTime'].astype(str), format = '%Y-%m-%d %H:%M:%S')

# Create a column for year and year and month
data1['Year'] = data1['DateTime'].map(lambda x:x.year)
data1['Month'] = data1['DateTime'].map(lambda x:x.month)
data1['Day'] = data1['DateTime'].map(lambda x:x.day)
data1['Hour'] = data1['DateTime'].map(lambda x:x.hour)

data1['YearM'] = pd.to_datetime(data1.DateTime).dt.to_period('m').astype(str)

data1.dtypes

# Rename columns for clarity
df2 = data1.rename({'CO(GT)' : 'CO',	'PT08.S1(CO)' : 'CO_s',	'NMHC(GT)' : 'NMHC',	'C6H6(GT)' : 'C6H6',
                 'PT08.S2(NMHC)' : 	'NMHC_s', 'NOx(GT)' : 'NOx', 'PT08.S3(NOx)' : 'NOx_s', 'NO2(GT)' : 'NO2', 'PT08.S4(NO2)': 'NO2_s',
                 'PT08.S5(O3)' : 'O3_s',	'T' : 'Temp',	'RH' : 'RH%', 'AH' : 'AH',
                 'DateTime' : 'DateTime', 'Month' : 'Month', 'Day': 'Day', 'Hour' : 'Hour',
                 'YearM' : 'YearM'}, axis = 1)

df2

df2.describe()

# Replace -200 with NaN
df2.replace(to_replace = -200, value = np.NaN, inplace = True)

# Heatmap of NaN values
sns.heatmap(df2.isnull(), yticklabels = False, cbar = False, cmap = 'Blues')

# Drop NMHC
df2.drop(['NMHC'], axis = 1, inplace = True)

# Correlation Heat Map
sns.heatmap(df2.corr(), annot = True)

print(df2.corr())

# Num of missing in each column
total_missing = df2.isnull().sum()

missing = total_missing > (len(df2)*.3)
missing = total_missing[missing]

# Variables with NaN values > 30% of all obs
print(missing)

#total_missing

# Find observations with null
#null_obs = []
#for index, row in df2.iterrows():
  #if row.isnull().sum() > len(df2.columns)*.10 :
    #null_obs.append(index)
    #df2 = df2.drop(index, axis=0)
#df22 = df2.drop(null_obs, axis=0)

## Filling all missing values with medians
# Filling missing value of CO with similar medians according to correlation
index_NaN_CO = np.where(df2['CO'].isnull())[0]

for i in index_NaN_CO :
    CO_med = df2["CO"].median()
    CO_pred = df2["CO"][((df2['CO_s'] == df2.iloc[i]["CO_s"]) & (df2['C6H6'] == df2.iloc[i]["C6H6"]))].median()
    if not np.isnan(CO_pred) :
        df2['CO'].iloc[i] = CO_pred
    else :
        df2['CO'].iloc[i] = CO_med

# Filling missing value of CO_s with similar medians according to correlation
index_NaN_COs = np.where(df2['CO_s'].isnull())[0]

for i in index_NaN_COs:
    COs_med = df2["CO_s"].median()
    COs_pred = df2["CO_s"][((df2['NMHC_s'] == df2.iloc[i]["NMHC_s"]) & (df2['C6H6'] == df2.iloc[i]["C6H6"]))].median()
    if not np.isnan(COs_pred) :
        df2['CO_s'].iloc[i] = COs_pred
    else :
        df2['CO_s'].iloc[i] = COs_med

# Filling missing value of C6H6 with similar medians according to correlation
index_NaN_C6H6 = np.where(df2['C6H6'].isnull())[0]

for i in index_NaN_C6H6 :
    C6H6_med = df2["C6H6"].median()
    C6H6_pred = df2["C6H6"][((df2['NMHC_s'] == df2.iloc[i]["NMHC_s"]) & (df2['CO'] == df2.iloc[i]["CO"]))].median()
    if not np.isnan(C6H6_pred):
        df2['C6H6'].iloc[i] = C6H6_pred
    else :
        df2['C6H6'].iloc[i] = C6H6_med

# Filling missing value of NMHC_s with similar medians according to correlation
index_NaN_NMHC_s = np.where(df2['NMHC_s'].isnull())[0]

for i in index_NaN_NMHC_s :
    NMHC_s_med = df2["NMHC_s"].median()
    NMHC_s_pred = df2["NMHC_s"][((df2['CO'] == df2.iloc[i]["CO"]) & (df2['C6H6'] == df2.iloc[i]["C6H6"]))].median()
    if not np.isnan(NMHC_s_pred) :
        df2['NMHC_s'].iloc[i] = NMHC_s_pred
    else :
        df2['NMHC_s'].iloc[i] = NMHC_s_med

# Filling missing value of NOx with similar medians according to correlation
index_NaN_NOx = np.where(df2['NOx'].isnull())[0]

for i in index_NaN_NOx :
    NOx_med = df2["NOx"].median()
    NOx_pred = df2["NOx"][((df2['O3_s'] == df2.iloc[i]["O3_s"]) & (df2['CO'] == df2.iloc[i]["CO"]))].median()
    if not np.isnan(NOx_pred) :
        df2['NOx'].iloc[i] = NOx_pred
    else :
        df2['NOx'].iloc[i] = NOx_med

# Filling missing value of NOx_s with similar medians according to correlation
index_NaN_NOx_s = np.where(df2['NOx_s'].isnull())[0]

for i in index_NaN_NOx_s :
    NOx_s_med = df2["NOx_s"].median()
    NOx_s_pred = df2["NOx_s"][((df2['O3_s'] == df2.iloc[i]["O3_s"]) & (df2['NMHC_s'] == df2.iloc[i]["NMHC_s"]))].median()
    if not np.isnan(NOx_s_pred) :
        df2['NOx_s'].iloc[i] = NOx_s_pred
    else :
        df2['NOx_s'].iloc[i] = NOx_s_med

# Filling missing value of NO2 with similar medians according to correlation
index_NaN_NO2 = np.where(df2['NO2'].isnull())[0]

for i in index_NaN_NO2 :
    NO2_med = df2["NO2"].median()
    NO2_pred = df2["NO2"][((df2['O3_s'] == df2.iloc[i]["O3_s"]) & (df2['NOx'] == df2.iloc[i]["NOx"]))].median()
    if not np.isnan(NO2_pred) :
        df2['NO2'].iloc[i] = NO2_pred
    else :
        df2['NO2'].iloc[i] = NO2_med

# Filling missing value of NO2_s with similar medians according to correlation
index_NaN_NO2_s = np.where(df2['NO2_s'].isnull())[0]

for i in index_NaN_NO2_s :
    NO2_s_med = df2["NO2_s"].median()
    NO2_s_pred = df2["NO2_s"][((df2['C6H6'] == df2.iloc[i]["C6H6"]) & (df2['NMHC_s'] == df2.iloc[i]["NMHC_s"]))].median()
    if not np.isnan(NO2_s_pred) :
        df2['NO2_s'].iloc[i] = NO2_s_pred
    else :
        df2['NO2_s'].iloc[i] = NO2_s_med

# Filling missing value of O3_s with similar medians according to correlation
index_NaN_O3_s = np.where(df2['O3_s'].isnull())[0]

for i in index_NaN_O3_s :
    O3_s_med = df2["O3_s"].median()
    O3_s_pred = df2["O3_s"][((df2['CO_s'] == df2.iloc[i]["CO_s"]) & (df2['NMHC_s'] == df2.iloc[i]["NMHC_s"]))].median()
    if not np.isnan(O3_s_pred) :
        df2['O3_s'].iloc[i] = O3_s_pred
    else :
        df2['O3_s'].iloc[i] = O3_s_med

# Filling missing values with median with respective column
df2[['Temp', 'RH%', 'AH']] = df2[['Temp', 'RH%', 'AH']].fillna(df2.median())

total_missing = df2.isnull().sum()
total_missing

df2.dtypes

df2.describe()

"""# Variable Selection and Plots"""

# New correlation
print(df2.corr())

# Correlation Heat Map
sns.heatmap(df2.corr())

# DF without time/date
df3 = df2.select_dtypes(exclude = ['object', 'datetime64[ns]'])

# Distributions for each variable
for column in df3.columns:
    plt.figure()
    sns.distplot(df3[column])

# Distributions for each variable
for column in df3.columns:
    plt.figure()
    sns.boxplot(df3[column])

# Linear plot with temp against all variables
for column in df3.columns:
    plt.figure()
    sns.jointplot(x = column, y = 'Temp', data = df3, kind = 'reg')

# Gas Concentrations across each month in both years
for column in df3.columns:
    plt.figure()
    ax = sns.pointplot(x = "Month", y = column, hue = "Year", data = df3)
    ax.set_xticklabels(ax.get_xticklabels(), rotation = 40, ha = "right", fontsize = 8)
    plt.tight_layout()
    plt.show()

# Plot with AH against all variables
for column in df3.columns:
    plt.figure()
    sns.jointplot(x = column, y = 'AH', data = df3, kind = 'reg')

# Combined plot of Temp and NO2_s vs date
fig, ax = plt.subplots()
sns.pointplot(x = "Month", y = 'Temp', hue = "Year", data = df3, palette = 'Blues')
ax2 = ax.twinx()
sns.pointplot(x = "Month", y = 'NO2_s', hue = "Year", data = df3, palette = 'Reds')

plt.show()

# Combined plot of AH and NO2_s vs date
fig, ax2 = plt.subplots()
sns.pointplot(x = "Month", y = 'AH', hue = "Year", data = df3, palette = 'Blues')
ax3 = ax2.twinx()
sns.pointplot(x = "Month", y = 'NO2_s', hue = "Year", data = df3, palette = 'Reds')

plt.show()

"""# Linear Regression - Temperature OLS

Temp = 0.4277911583087839 + 0.10486557 * NO2_s - 0.03218797 * NOx - 0.59544465 * RH% + 0.66706038 * AH - 0.01989868 * Year
"""

# Scale dataframe
mm = MinMaxScaler()
df_scaled = pd.DataFrame(mm.fit_transform(df3), columns = df3.columns)
print(df_scaled)
print(df_scaled.describe())
print(df_scaled.corr())

# Define X and Y
X = df_scaled[['NO2_s', 'NOx', 'RH%', 'AH', 'Year']]
Y = df_scaled['Temp']

#X

s = StandardScaler()

# Create testing and training data
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size = 0.25, random_state = 10)
print(X_train.shape)
print(X_test.shape)
print(Y_train.shape)
print(Y_test.shape)

# Fit linear model
lin_model = LinearRegression()
lin_model.fit(X_train, Y_train)

# Evaluation for Training
y_train_predict = lin_model.predict(X_train)
rmse = (np.sqrt(mean_squared_error(Y_train, y_train_predict)))
r2 = r2_score(Y_train, y_train_predict)

print("The model performance for training set")
print("--------------------------------------")
print('RMSE is {}'.format(rmse))
print('R2 score is {}'.format(r2))
print("\n")

# Evaluation for Testing
y_test_predict = lin_model.predict(X_test)
rmse = (np.sqrt(mean_squared_error(Y_test, y_test_predict)))
r2 = r2_score(Y_test, y_test_predict)

print("The model performance for testing set")
print("--------------------------------------")
print('RMSE is {}'.format(rmse))
print('R2 score is {}'.format(r2))

# OLS Summary
X_train_off = sm.add_constant(X_train)
smRegression = sm.OLS(Y_train, X_train_off)

model = smRegression.fit()
print(model.summary())

print(lin_model.coef_)
print(lin_model.intercept_)

"""# SGDRegression - Temp"""

# Hypertune parameters
sgdr = SGDRegressor(alpha = 0.0025, epsilon = 0.09, eta0 = 0.1,
                    max_iter = 10000, penalty = 'elasticnet', )

sgdr.fit(X_train, Y_train)

score = sgdr.score(X_train, Y_train)
print("R-squared:", score)

ypred = sgdr.predict(X_test)

# Calculate MSE and RMSE
mse = mean_squared_error(Y_test, ypred)
print("MSE: ", mse)
print("RMSE: ", mse**(1/2.0))

x_ax = range(len(Y_test))
plt.plot(x_ax, Y_test, label = "original")
plt.plot(x_ax, ypred, label = "predicted")
plt.title("Air Quality Test vs Prediction (Temp)")
plt.xlabel('X-axis')
plt.ylabel('Y-axis')
plt.legend(loc = 'best', fancybox = True, shadow = True)
plt.grid(True)
plt.show()

"""#  Decision Tree Regressor - Temp"""

df3.round(decimals = 5)

# Define X and Y
X = df_scaled[['NO2_s', 'NOx', 'RH%', 'AH', 'Year']]
Y = df_scaled['Temp']

X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size = 0.4, random_state = 10)

# Creating and fitting regressor
regressor = DecisionTreeRegressor()
regressor.fit(X_train, Y_train)

# Predicting metrics
predictions = regressor.predict(X_test)

print("R2 square = ", r2_score(Y_test, predictions))
print("MSE = ", mean_squared_error(Y_test, predictions))
print("MAE = ", mean_absolute_error(Y_test, predictions))
print("Explained variance score = ", explained_variance_score(Y_test, predictions))

# Tree with base parameters
dot_data = tree.export_graphviz(regressor, out_file = None,
                                feature_names = X.columns,
                                class_names = Y.unique(),
                                filled = True, rounded = True,
                                special_characters = True)
graph = graphviz.Source(dot_data)
graph

#fig = plt.figure(figsize=(25,20))
#dot_data = dtreeviz(regressor, X_train, Y_train,
#                                feature_names = X.columns,
#                                target_name = Y.unique())
#dot_data

# Fine tuning DecisionTreeRegressor()
dt_pipe = Pipeline([('mms', MinMaxScaler()),
                     ('dt', DecisionTreeRegressor())])
params = [{'dt__max_depth': [3, 5, 10, 15],
         'dt__min_samples_leaf': [2, 3, 5]}]

gs_dt = GridSearchCV(dt_pipe,
                     param_grid = params,
                     scoring = 'r2',
                     cv = 5)
gs_dt.fit(X, Y)
print(gs_dt.best_params_)

# Find best model score
print('R2:', gs_dt.score(X, Y))

# Tree with fine tuned parameters
regressor1 = DecisionTreeRegressor(max_depth = 15, min_samples_leaf = 2)
regressor1.fit(X_train, Y_train)

dot_data = tree.export_graphviz(regressor1, out_file = None,
                                feature_names = X.columns,
                                class_names = Y.unique(),
                                filled = True, rounded = True,
                                special_characters = True)
graph = graphviz.Source(dot_data)
graph

# Predicting metrics after optimization
predictions = gs_dt.predict(X_test)

print("R2 square = ", r2_score(Y_test, predictions))
print("MSE = ", mean_squared_error(Y_test, predictions))
print("MAE = ", mean_absolute_error(Y_test, predictions))
print("Explained variance score = ", explained_variance_score(Y_test, predictions))

"""# Random Forest Regressor - Temp


"""

# Create and fit RF regressor
rf = RandomForestRegressor()
rf.fit(X_train, Y_train)

# Predict metrics using base parameters
predictions = rf.predict(X_test)

print("R2 square = ", r2_score(Y_test, predictions))
print("MSE = ", mean_squared_error(Y_test, predictions))
print("MAE = ", mean_absolute_error(Y_test, predictions))
print("Explained variance score = ", explained_variance_score(Y_test, predictions))

params = {'max_depth': [3, 5, 10, 15],
          'n_estimators': [50, 150, 250]}
#scoring = ['r2', 'explained_variance', 'max_error', 'neg_mean_absolute_error', 'neg_mean_squared_error']
grid = GridSearchCV(rf, params, cv = 5, scoring = 'r2', return_train_score = False)
grid.fit(X, Y)

print(grid.best_params_)
# Find best model score
print('R2:', grid.score(X, Y))

y_predictions = grid.predict(X_test)

print("R2 square = ", r2_score(Y_test, predictions))
print("MSE = ", mean_squared_error(Y_test, predictions))
print("MAE = ", mean_absolute_error(Y_test, predictions))
print("Explained variance score = ", explained_variance_score(Y_test, predictions))

"""# AdaBoost Regressor - Temp"""

# Create and fitAdaBoost regressor
adab = AdaBoostRegressor()
adab.fit(X_train, Y_train)

# Make predictions based on AdaBoost predictions
predictions = adab.predict(X_test)

print("R2 square = ", r2_score(Y_test, predictions))
print("MSE = ", mean_squared_error(Y_test, predictions))
print("MAE = ", mean_absolute_error(Y_test, predictions))
print("Explained variance score = ", explained_variance_score(Y_test, predictions))

# Tune parameters
params = {'n_estimators':[50, 150, 250],
         'learning_rate':[.001, 0.01, .1, 1],
          'random_state':[5]}

grid1 = GridSearchCV(adab, params, scoring = 'r2', cv = 5)
grid1.fit(X, Y)

print(grid1.best_params_)
# Find best model score
print('R2:', grid1.score(X, Y))

# Predictions using tuned parameters
predictions = grid1.predict(X_test)

print("R2 square = ", r2_score(Y_test, predictions))
print("MSE = ", mean_squared_error(Y_test, predictions))
print("MAE = ", mean_absolute_error(Y_test, predictions))
print("Explained variance score = ", explained_variance_score(Y_test, predictions))

"""# XGBoost Regressor - Temp"""

xgb1 = xgb.XGBRegressor()
xgb1.fit(X_train, Y_train)

# Predictions before tuning
predictions = xgb1.predict(X_test)

print("R2 square = ", r2_score(Y_test, predictions))
print("MSE = ", mean_squared_error(Y_test, predictions))
print("MAE = ", mean_absolute_error(Y_test, predictions))
print("Explained variance score = ", explained_variance_score(Y_test, predictions))

xgb_model = xgb.XGBRegressor(n_jobs = multiprocessing.cpu_count() // 2)
clf = GridSearchCV(xgb_model, {'max_depth': [3, 5, 10, 15], 'n_estimators': [50, 150, 250]},
                   verbose = 2, n_jobs = 2, cv = 10)
clf.fit(X, Y)
print(clf.best_score_)
print(clf.best_params_)

# Predictions using tuned parameters
predictions = clf.predict(X_test)

print("R2 square = ", r2_score(Y_test, predictions))
print("MSE = ", mean_squared_error(Y_test, predictions))
print("MAE = ", mean_absolute_error(Y_test, predictions))
print("Explained variance score = ", explained_variance_score(Y_test, predictions))

"""# Classification Metrics - Decision Tree"""

# Transform Temp into a categorical variable
df3.describe()['Temp']
subTemp = pd.cut(df3.Temp, bins = [-2, 12.025000, 17.750000, 24.075000, 50],
                 labels = ['Min', '25%', '50%', '75% +'])

df3.insert(9, 'TempGroup', subTemp)

df3['TempGroup'].value_counts(normalize = True)

# Create X, Y
featureCol = ['NO2_s', 'NOx', 'RH%', 'AH', 'Year']
X = df3[featureCol]
Y = df3.TempGroup

# Set training and testing parameters
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size = 0.3, random_state = 1)

# Define and fit classifier
clf = DecisionTreeClassifier()
clf.fit(X_train, Y_train)

# Predictions before optimizing
predictions = clf.predict(X_test)
predicted_probas = clf.predict_proba(X_test)

print(classification_report(Y_test, predictions))
print('Predicted labels: ', predictions)
print('Accuracy: ', accuracy_score(Y_test, predictions))

# Tree with base parameters
dot_data = tree.export_graphviz(clf, out_file = None,
                                feature_names = X.columns,
                                class_names = Y.unique(),
                                filled = True, rounded = True,
                                special_characters = True)
graph = graphviz.Source(dot_data)
graph

# Matrix, ROC, precision-recall before optimizing
skplt.metrics.plot_confusion_matrix(Y_test, predictions)
skplt.metrics.plot_roc(Y_test, predicted_probas)
skplt.metrics.plot_precision_recall_curve(Y_test, predicted_probas)
plt.show()

#Hypertune parameters
dt_pipe = Pipeline([('mms', MinMaxScaler()), ('dt', DecisionTreeClassifier())])
params = [{'dt__max_depth': [5, 10, 12, 15], 'dt__min_samples_leaf': [2, 3, 5]}]

gs_dt = GridSearchCV(dt_pipe, param_grid = params, scoring = 'accuracy', cv = 5)
gs_dt.fit(X, Y)

# Print results
print(gs_dt.best_params_)
print(gs_dt.score(X, Y))

predictions = gs_dt.predict(X_test)
predicted_probas = gs_dt.predict_proba(X_test)

print(classification_report(Y_test, predictions))
print('Predicted labels: ', predictions)
print('Accuracy: ', accuracy_score(Y_test, predictions))

# Matrix, ROC, precision-recall before optimizing
skplt.metrics.plot_confusion_matrix(Y_test, predictions)
skplt.metrics.plot_roc(Y_test, predicted_probas)
skplt.metrics.plot_precision_recall_curve(Y_test, predicted_probas)
plt.show()

# Tree with optimized parameters
dt2 = DecisionTreeClassifier(min_samples_leaf = 3, max_depth = 12)
clf2 = dt2.fit(X_train, Y_train)

# Tree with base parameters
dot_data = tree.export_graphviz(clf2, out_file = None,
                                feature_names = X.columns,
                                class_names = Y.unique(),
                                filled = True, rounded = True,
                                special_characters = True)
graph = graphviz.Source(dot_data)
graph

"""# Classification Metrics - Random Forest"""

# Create and fit classifier
rf = RandomForestClassifier()
clf1 = rf.fit(X_train, Y_train)

# Prior to optimizing
dot_data = export_graphviz(clf1.estimators_[0],
                feature_names=X.columns,
                filled=True,
                rounded=True)

graph = graphviz.Source(dot_data)
graph

# Predictions before optimization
predictions = rf.predict(X_test)
predicted_probas = rf.predict_proba(X_test)

print(classification_report(Y_test, predictions))
print('Predicted labels: ', predictions)
print('Accuracy: ', accuracy_score(Y_test, predictions))

skplt.metrics.plot_confusion_matrix(Y_test, predictions)
skplt.metrics.plot_roc(Y_test, predicted_probas)
skplt.metrics.plot_precision_recall_curve(Y_test, predicted_probas)
plt.show()

# Optimize parameters
grid = GridSearchCV(rf, {'max_depth': [5, 10, 12, 15],
          'n_estimators': [50, 150, 250],
          'max_features': ['sqrt', 'log2']}, scoring = 'accuracy', return_train_score = False)

grid.fit(X, Y)

# Print results
print(grid.best_params_)
print(grid.score(X, Y))

# Predictions before optimization
predictions = grid.predict(X_test)

print(classification_report(Y_test, predictions))
print('Predicted labels: ', predictions)
print('Accuracy: ', accuracy_score(Y_test, predictions))

# Display results from grid search
plot.grid_search(grid.cv_results_, change = 'n_estimators', kind = 'bar')

# Tree after optimization
rf = RandomForestClassifier(n_estimators = 50, max_depth = 12, max_features = 'log2')
clf2 = rf.fit(X_train, Y_train)
dot_data = export_graphviz(clf2.estimators_[0],
                feature_names=X.columns,
                filled=True,
                rounded=True)

graph = graphviz.Source(dot_data)
graph

# Predictions after optimization
predictions = grid.predict(X_test)
predicted_probas = grid.predict_proba(X_test)

print(classification_report(Y_test, predictions))
print('Predicted labels: ', predictions)
print('Accuracy: ', accuracy_score(Y_test, predictions))

skplt.metrics.plot_confusion_matrix(Y_test, predictions)
skplt.metrics.plot_roc(Y_test, predicted_probas)
skplt.metrics.plot_precision_recall_curve(Y_test, predicted_probas)
plt.show()

"""# Classification Metrics - AdaBoost"""

adab = AdaBoostClassifier(random_state = 5)
clf1 = adab.fit(X_train, Y_train)

# Report before optimizing
predictions = adab.predict(X_test)
predicted_probas = adab.predict_proba(X_test)

print(classification_report(Y_test, predictions))
print('Predicted labels: ', predictions)
print('Accuracy: ', accuracy_score(Y_test, predictions))

# Plot classification
skplt.metrics.plot_confusion_matrix(Y_test, predictions)
skplt.metrics.plot_roc(Y_test, predicted_probas)
skplt.metrics.plot_precision_recall_curve(Y_test, predicted_probas)
plt.show()

# Create XGBoost model and parameterize
clf = GridSearchCV(adab, {'n_estimators':[50, 150, 250],
                          'learning_rate':[.001, 0.01, .1, 1],
                          'random_state':[5]}, verbose = 1, n_jobs = 2, cv = 10)

# Fit model and print results
clf.fit(X, Y)
print(clf.best_score_)
print(clf.best_params_)

# Report after optimizing
predictions = clf.predict(X_test)
predicted_probas = clf.predict_proba(X_test)

print(classification_report(Y_test, predictions))
print('Predicted labels: ', predictions)
print('Accuracy: ', accuracy_score(Y_test, predictions))

# Plot classification
skplt.metrics.plot_confusion_matrix(Y_test, predictions)
skplt.metrics.plot_roc(Y_test, predicted_probas)
skplt.metrics.plot_precision_recall_curve(Y_test, predicted_probas)
plt.show()

"""# Classification Metrics - XGBoost"""

xgb1 = xgb.XGBClassifier(random_state = 5)
xgb1.fit(X_train, Y_train)

# Report after optimizing
y_pred = xgb1.predict(X)
y_probs = xgb1.predict_proba(X)

print(classification_report(Y, y_pred))
print('Predicted labels: ', y_pred)
print('Accuracy: ', accuracy_score(Y, y_pred))

# Plot classification
skplt.metrics.plot_confusion_matrix(Y, y_pred)
skplt.metrics.plot_roc(Y, y_probs)
skplt.metrics.plot_precision_recall_curve(Y, y_probs)
plt.show()

# Create XGBoost model and parameterize
xgb_model = xgb.XGBClassifier(n_jobs = multiprocessing.cpu_count() // 2)
clf = GridSearchCV(xgb_model, {'max_depth': [5, 10, 15],
                               'n_estimators': [25, 50, 100],
                               'random_state': [5]}, verbose = 1, n_jobs = 2, cv = 10)

# Fit model and print results
clf.fit(X, Y)
print(clf.best_score_)
print(clf.best_params_)

# Report after optimizing
y_pred = clf.predict(X)
y_probs = clf.predict_proba(X)

print(classification_report(Y, y_pred))
print('Predicted labels: ', y_pred)
print('Accuracy: ', accuracy_score(Y, y_pred))

# Plot classification
skplt.metrics.plot_confusion_matrix(Y, y_pred)
skplt.metrics.plot_roc(Y, y_probs)
skplt.metrics.plot_precision_recall_curve(Y, y_probs)
plt.show()

# Plot tree
xgb1 = xgb.XGBClassifier(max_depth = 2, n_estimators = 200,
                         n_jobs=multiprocessing.cpu_count() // 2)
clf1 = xgb1.fit(X_train, Y_train)
xgb.plot_tree(xgb1)

