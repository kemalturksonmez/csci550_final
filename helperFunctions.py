from pymongo import MongoClient
import numpy as np
import pandas as pd
import random
from numpy.random import shuffle
from DataProcessing import DataProcessing
from cluster import Cluster
np.set_printoptions(threshold=np.inf)



# gets clusters for flavor town and cat
# cat - category matrix
# flavorTown - flavorTown matrix
# returns two tuples:
# flavor_centers - centers of flavor clusters
# flavor_clusters - members of flavor clusters
# cat_centers - centers of category clusters
# cat_clusters - members of category clusters
def getClusters(cat, flavorTown):
    flavor_centers, flavor_clusters = Cluster().get_centroids(flavorTown, 10, 0.001)
    cat_centers, cat_clusters = Cluster().get_centroids(cat, 7, 0.001)
    return (cat_centers, cat_clusters), (flavor_centers, flavor_clusters)

# creates a shuffled array of k indicies that will be used for splitting data
# utility - user matrix
# returns:
# shuffledArray - shuffled array of indicies
def shuffleArray(utility):
    indicies = np.zeros(len(utility))
    for i in range(len(indicies)):
        indicies[i] = i
    shuffle(indicies)
    return indicies

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

# splits a 2D array by removing last column
# returns:
# newMatrix - updated 2D array
# lastCol - last column
def splitColumn(matrix):
    lastCol = matrix[:,-1]
    print(matrix)
    newMatrix = matrix[:,:-1]
    print(newMatrix)
    return newMatrix, lastCol

# orders members of a list by similarity to user
# row - individual row from test set
# cluster - list of all the items in a cluster
def getSortedItems(row, cluster):
    c = Cluster()
    distanceList = []
    for item in cluster:
        distanceList.append([c.squared_euclidean_distance(row, item), tuple(item)])
    distanceList.sort(key=lambda x: x[0]) 
    print(distanceList)
    return distanceList

# testData - contains test users
# flavClustGroup -> tuple = Contains clusters centers and clusters of the flavor group
# flavClustGroup -> 0 = Cluster centers
# flavClustGroup -> 1 = Dictionary containing clusters, key is the tuple of the clusters centers
# catClustGroup -> tuple = Contains clusters centers and clusters of the category group
# catClustGroup -> 0 = Cluster centers
# catClustGroup -> 1 = Dictionary containing clusters, key is the tuple of the clusters centers
# returns:
def getDistanceList(testData, flavClustGroup, catClustGroup):
    c = Cluster()
    userClusterList = []
    for row in testData:
        # Find the closest flavor cluster
        rowFlavDistance = c.find_clusters_distance_sorted(row, flavClustGroup[0])
        # # Find the category cluster thats closest to the flavor cluster
        flavCatDistance = c.find_clusters_distance_sorted(rowFlavDistance[1], catClustGroup[0])
        print(row)
        print()
        # # Get the closest members to the user in a given cluster
        getSortedItems(row, catClustGroup[1][flavCatDistance[1]])


# Runs cross validation on data
def crossValidation(utility, cat):
    cvNum = 1
    shuffledArray = shuffleArray(utility)
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
        flavClustGroup, catClustGroup = getClusters(cat, trainData)
        getDistanceList([testData[0]], flavClustGroup, catClustGroup)
        


