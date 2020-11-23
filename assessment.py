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


#This file will contain our method for model evaluation

#Process:
#1 - begin loop for k fold cv (or LOOCV)
    #2 - split data into training-testing
    #3 - create model using training
    #4 - for each test user, remove highest rated restaurant(?)
    #5 - identify discrepency b/w prediction and missing restaurant



# Runs cross validation on data
def crossValidation(utility, cat):
    cvNum = 1
    shuffledArray = hf.shuffleArray(utility)
    d = DataProcessing()
    c = Cluster()
    # attach ids for users
    # utility = d.attachId(utility)
    for currIndex in range(cvNum):
        # create flavor matrix
        flavorTown = d.createFlavorMatrix(utility, cat)
        # attach ids
        flavorTown = d.attachId(flavorTown)

        cat = d.attachId(cat)
        # split data
        testData, trainData = testTrainSplit(flavorTown, shuffledArray, currIndex)
        
        # create clusters
        flavClustGroup, catClustGroup = hf.getClusters(cat, trainData)
        hf.getDistanceList([testData[0]], flavClustGroup, catClustGroup)

# splits data based on a shuffled array of indicies
# utility - user matrix
# shuffledArray - shuffled array of indicies
def testTrainSplit(utility, shuffledArray, currIndex):
    utilLength = int(len(utility)/10)
    numRows = ((utilLength * currIndex) + utilLength) - (utilLength * currIndex)

    testData = np.zeros((numRows,len(utility[0])))
    for i in range((utilLength * currIndex),(utilLength * currIndex) + utilLength):
        testData[i - (utilLength * currIndex)] = utility[int(shuffledArray[i])]

    trainData = np.zeros((len(utility) - numRows,len(utility[0])))
    trainTracker = 0
    for i in range(0,(utilLength * currIndex)):
        trainData[trainTracker] = utility[int(shuffledArray[i])]
        trainTracker += 1

    for i in range((utilLength * currIndex) + utilLength, len(utility)):
        trainData[trainTracker] = utility[int(shuffledArray[i])]
        trainTracker += 1
    return testData, trainData
