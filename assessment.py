from pymongo import MongoClient
import numpy as np
import pandas as pd
import random
from numpy.random import shuffle
from DataProcessing import DataProcessing
from numpy.random import shuffle
from cluster import Cluster
from model import Model
import helperFunctions as hf

# def splitData(data,k,i):
#     train = []
#     test = []
#     for j = range(len()):
#     for j = range(len()):
#     for j = range(len()):
#     return train,test

#This file will contain our method for model evaluation

#Process:
#1 - begin loop for k fold cv (or LOOCV)
    #2 - split data into training-testing
    #3 - create model using training
    #4 - for each test user, remove highest rated restaurant(?)
    #5 - identify discrepency b/w prediction and missing restaurant

k = 1
dp = DataProcessing()
shuffledArray = hf.shuffleArray(dp.getUtilMatrix())

cumulativeEvaluationValue = 0
totalEvaluations = 0
# Runs cross validation on data
users, restaurants, cat, utility, flavorTown = dp.getAllFiles() #[users, restaurants, cat, utility, flavorTown]

for i in range(k):
    print("starting k-folds")
    #Split train-test
    testUtil, trainUtil = hf.testTrainSplit(utility, shuffledArray, i)

    print("creating training")
    #create training model
    m = Model()
    m.utility = trainUtil
    m.flavorTown = dp.createFlavorMatrix(trainUtil,cat)
    m.createFlavorAndAttachIds()

    print("removing reviews")
    #Remove a review
    testUserNorm = dp.getNormalizedUtilMat(testUtil)
    removedRestaurants = []

    for u in range(len(testUserNorm)):
        notZeroIndices = np.where(testUserNorm[u] != 0)[0]
        positiveIndices = np.where(testUserNorm[u] > 0)[0]
        r = np.random.randint(low=0,high=len(notZeroIndices))
        removedRestaurants.append(notZeroIndices[r])
        testUtil[u][notZeroIndices[r]] = 0

    print("recommending")
    #Get test recommendations
    for count,user in enumerate(testUtil):
        recs,ids = m.recommend(np.asarray([user]))
        print(recs,ids)
        
        if removedRestaurants[count] in ids:
            if removedRestaurants[count] in positiveIndices:
                cumulativeEvaluationValue+=1
            totalEvaluations+=1


finalEvalValue = cumulativeEvaluationValue/totalEvaluations
print("SUCCESS RATE:")
print(finalEvalValue)

