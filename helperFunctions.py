from pymongo import MongoClient
import numpy as np
import pandas as pd
import random
from numpy.random import shuffle
from DataProcessing import DataProcessing
from cluster import Cluster

# gets clusters for flavor town and cat
# cat - category matrix
# flavorTown - flavorTown matrix
# returns two tuples:
# flavor_centers - centers of flavor clusters
# flavor_clusters - members of flavor clusters
# cat_centers - centers of category clusters
# cat_clusters - members of category clusters
def getClusters(cat, flavorTown):
    flavor_centers, flavor_clusters = Cluster().get_centroids(flavorTown, 100, 0.01)
    cat_centers, cat_clusters = Cluster().get_centroids(cat, 100, 0.01)
    
    flavor_centers, flavor_clusters = removeEmpty(flavor_centers, flavor_clusters)
    cat_centers, cat_clusters = removeEmpty(cat_centers, cat_clusters)
    

    return (cat_centers, cat_clusters), (flavor_centers, flavor_clusters)

def removeEmpty(arr,dic):
    newArr = []
    newDic = dict()
    for x,y in zip(arr,dic):
        if len(dic[y]) != 0:
            newArr.append(x)
            newDic[y] = dic[y] 

    return newArr, newDic

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

# splits data based on a shuffled array of indicies
# utility - user matrix
# shuffledArray - shuffled array of indicies
def testTrainSplit(utility, shuffledArray, currIndex):
    utilLength = int(len(utility[0])/600)
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
