# -*- coding: utf-8 -*-
#This document was generated by Pia Wolffram. 
#However, other sources have been used.
#These sources are written below and indicated at the specific places.

#Sources:
#Fraj (2018): In Depth: Parameter tuning for SVC (https://medium.com/all-things-ai/in-depth-parameter-tuning-for-svc-758215394769)
#Gis - Exchange (2021): Performing supervised classification on Sentinel Images (https://gis.stackexchange.com/questions/373720/performing-supervised-classification-on-sentinel-images)
#Hatari Lab (2020): Extract point value from a raster file with Python, Geopandas and Rasterio (https://hatarilabs.com/ih-en/extract-point-value-from-a-raster-file-with-python-geopandas-and-rasterio-tutorial)
#Krishnaik06 (2020): Sklearn Pipeline (https://github.com/krishnaik06/Pipelines-Using-Sklearn/blob/master/SklearnPipeline.ipynb

import geopandas as gpd
import pandas as pd
import numpy as np
import rasterio
import matplotlib.pyplot as plt
from rasterstats import zonal_stats
import os

from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV
from sklearn.experimental import enable_halving_search_cv
from sklearn.model_selection import HalvingGridSearchCV

from sklearn.metrics import accuracy_score
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import f1_score

#################################################################################

#PREPROCESSING
#Other sources: Gis - Exchange (2021)
#Create geodataframe from the points

pointfile = '../groundtruth_data/gbin.shp'
s2folder = r'../input_data/'
df = gpd.read_file(pointfile)

#Iterate through each band-file, exctract the data-points, merge dataframe with points and input images into one dataframe
columns = []
for root, folders, files in os.walk(s2folder):
    for file in files:
        f = os.path.join(root, file)
        stats = ['min']
        df2 = pd.DataFrame(zonal_stats(vectors=df['geometry'], raster=f, stats=stats))
        column_name = ['{0}_{1}'.format(stat, file.split('.')[0]) for stat in stats]
        columns.append(column_name[0])
        df2.columns=column_name
        df = df.join(df2)

#Split data into train and test (80, 20)
train = df.sample(frac = 0.8)
test = df.drop(train.index)

#Create a list of lists: for each row there are 4 (number of bands) entries
X = train[columns].values.tolist() 
#Class labels for X
y = train['id'].tolist()

#Create the test dataset
Xtest = test[columns]
ytest = test['id']

#################################################################################

#SUPPORT VECTOR MACHINE
#Other sources: Fraj (2018)
#Train with parameter grid and halving grid search
pipe = make_pipeline(StandardScaler(), SVC())
grid_param = [
    { "svc": [SVC()],
     "svc__kernel": ('linear', 'rbf', 'poly', 'sigmoid', 'precomputed'),
     "svc__C": [0.001, 0.1, 1, 10, 100, 1000],
     "svc__gamma": [0.1, 1, 10, 100, 'scale', 'auto'],
     }]

gridsearch = HalvingGridSearchCV(pipe,grid_param)
svm_model = gridsearch.fit(X,y)
svm_best = svm_model.best_estimator_
print(svm_best)

#Test
average = 'binary' #'binary or 'micro', 'macro'
ypredSVM = svm_best.predict(Xtest)
print("The mean accuracy of the model is:", accuracy_score(ytest, ypredSVM))
print("The mean precision of the model is:", precision_score(ytest, ypredSVM, average=average))
print("The mean recall of the model is:", recall_score(ytest, ypredSVM, average=average))
print("The mean f1 score of the model is:", f1_score(ytest, ypredSVM, average=average))


#K-NEAREST-NEIGHBOR-MODEL
#Other sources: Fraj (2018)
#Train with parameter grid and halving grid search
pipe = make_pipeline(StandardScaler(), KNeighborsClassifier())
grid_param = [
                {"kneighborsclassifier": [KNeighborsClassifier()],
                 "kneighborsclassifier__n_neighbors": [1,2,4,6,8,10,12,14,16,18,20],
                 "kneighborsclassifier__weights": ('uniform', 'distance'),
                 "kneighborsclassifier__metric": ('euclidean', 'manhattan', 'minkowski')
                 }]
gridsearch = HalvingGridSearchCV(pipe, grid_param, random_state=0)
knn_model = gridsearch.fit(X,y)
knn_best = knn_model.best_estimator_
print(knn_best)

#Test
average = 'binary' #'binary or 'micro', 'macro'
ypredKNN = knn_best.predict(Xtest)
print("The mean accuracy of the model is:", accuracy_score(ytest, ypredKNN))
print("The mean precision of the model is:", precision_score(ytest, ypredKNN, average=average))
print("The mean recall of the model is:", recall_score(ytest, ypredKNN, average=average))
print("The mean f1 score of the model is:", f1_score(ytest, ypredKNN, average=average))

#RANDOM FOREST MODEL
#Other sources: Fraj (2018)
#Train with parameter grid and halving grid search
pipe = make_pipeline((RandomForestClassifier()))
grid_param = [
                {"randomforestclassifier": [RandomForestClassifier()],
                 "randomforestclassifier__n_estimators": [10, 100, 1000],
                 "randomforestclassifier__max_features": ['auto', 'sqrt', 10, 100, 1000]}]
gridsearch = HalvingGridSearchCV(pipe, grid_param, random_state=0)
rf_model = gridsearch.fit(X,y)
rf_best = rf_model.best_estimator_ 
print(rf_best)

#Test
average = 'binary' #'binary or 'micro', 'macro'
ypredRF = rf_best.predict(Xtest)
print("The mean accuracy of the model is:", accuracy_score(ytest, ypredRF))
print("The mean precision of the model is:", precision_score(ytest, ypredRF, average=average))
print("The mean recall of the model is:", recall_score(ytest, ypredRF, average=average))
print("The mean f1 score of the model is:", f1_score(ytest, ypredRF, average=average))

#################################################################################

#Open band files 
b2 = rasterio.open(os.path.join(s2folder, 'B02_20221102T084019_clipped.tif')).read()
b2 = b2[0,:,:] 
b3 = rasterio.open(os.path.join(s2folder, 'B03_20221102T084019_clipped.tif')).read()
b3 = b3[0,:,:]
b4 = rasterio.open(os.path.join(s2folder, 'B04_20221102T084019_clipped.tif')).read()
b4 = b4[0,:,:]
b8 = rasterio.open(os.path.join(s2folder, 'B08_20221102T084019_clipped.tif')).read()
b8 = b8[0,:,:]

bands = np.dstack((b2,b3,b4,b8))
bands = bands.reshape(int(np.prod(bands.shape)/4),4)

#Make predictions 
model = knn_best
r = model.predict(bands) 
r = r.reshape(b2.shape)

#Save result to file
b2src = rasterio.open(os.path.join(s2folder, 'B02_20221102T084019_clipped.tif'))
with rasterio.Env():
    profile = b2src.profile
    profile.update(
        dtype=rasterio.uint8,
        count=1,
        compress='lzw')
    with rasterio.open('knn_multi.tif', 'w', **profile) as dst:
        dst.write(r.astype(rasterio.uint8), 1)