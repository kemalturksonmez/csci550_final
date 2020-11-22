from pymongo import MongoClient
import numpy as np
import pandas as pd
import random
from numpy.random import shuffle
from DataProcessing import DataProcessing
from cluster import Cluster
np.set_printoptions(threshold=np.inf)

def createInfo(cityName):
    d = DataProcessing()

    users, restaurants = d.initialDataProcessing(cityName)
    cat, utility = d.createMatrices()
    return users, restaurants, cat, utility

def getClusters(cat, flavorTown):
    flavor_centers, flavor_clusters = Cluster().get_centroids(flavorTown, 10, 0.001)
    cat_centers, cat_clusters = Cluster().get_centroids(cat, 7, 0.001)
    return (flavor_centers, flavor_clusters), (cat_centers, cat_clusters)

def shuffleArray(utility):
    indicies = np.zeros(len(utility))
    for i in range(len(indicies)):
        indicies[i] = i
    shuffle(indicies)
    return indicies

def stratifiedSplit(utility, shuffledArray, currIndex):
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

def splitColumn(matrix):
    lastCol = matrix[:,-1]
    print(matrix)
    newMatrix = matrix[:,:-1]
    print(newMatrix)
    return newMatrix, lastCol

def getSortedItems(row, cluster):
    c = Cluster()
    distanceList = []
    for item in cluster:
        distanceList.append([c.squared_euclidean_distance(row, item), tuple(item)])
    distanceList.sort(key=lambda x: x[0]) 
    print(distanceList)

def getDistanceList(testData, flavClustGroup, catClustGroup):
    c = Cluster()
    userClusterList = []
    for row in testData:
        flavDistance = c.find_clusters_distance_sorted(row, flavClustGroup[0])
        catDistance = c.find_clusters_distance_sorted(row, catClustGroup[0])
        userClusterList.append((row, flavDistance[1], catDistance[1]))
        getSortedItems(row, flavClustGroup[1][flavDistance[1]])

    # for user in userClusterList:
    #     print(flavClustGroup)
        # for clusterMember in flavClustGroup[1][user[1]]:
        #     getSortedItems(user[0], clusterMember)
    # print(userClusterList)
        


def crossValidation(utility, cat):
    cvNum = 1
    shuffledArray = shuffleArray(utility)
    d = DataProcessing()
    c = Cluster()
    # attach ids for users
    # utility = d.attachId(utility)
    for currIndex in range(cvNum):
        # get flavor matrix
        flavorTown = d.createFlavorMatrix(utility, cat)
        # attach ids
        flavorTown = d.attachId(flavorTown)
        cat = d.attachId(cat)
        # split data
        testData, trainData = stratifiedSplit(flavorTown, shuffledArray, currIndex)
        
        # create clusters
        flavClustGroup, catClustGroup = getClusters(cat, trainData)
        getDistanceList([testData[0]], flavClustGroup, catClustGroup)
        

# users, restaurants, cat, utility, flavorTown = createInfo("Montreal")
users, restaurants, cat, utility = DataProcessing().getAllFiles()
# attach ids to data points
crossValidation(utility, cat)


