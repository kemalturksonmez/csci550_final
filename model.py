from pymongo import MongoClient
import numpy as np
import pandas as pd
import random
from numpy.random import shuffle
from DataProcessing import DataProcessing
from cluster import Cluster
import helperFunctions as hf

class Model():

    #Creates base model
    def __init__(self,city = None):
        self.users = None
        self.restaurants = None
        self.cat = None
        self.utility = None
        self.flavorTown = None
        self.dp = DataProcessing()
        self.cluster = Cluster()

        if city is None:
            self.users, self.restaurants, self.cat, self.utility, self.flavorTown = self.dp.getAllFiles()         
            self.createFlavorAndAttachIds() 
        elif type(city) == type('string'):
            self.users, self.restaurants = self.dp.initialDataProcessing(city)
            self.cat, self.utility = self.dp.createMatrices()
            self.flavorTown = self.dp.createFlavorMatrix(self.utility,self.cat)
            # write flavor matrix
            self.dp.writeFlavorMatrix(self.flavorTown)
            self.createFlavorAndAttachIds()
        
        



    # flavClustGroup -> tuple = Contains clusters centers and clusters of the flavor group
    # flavClustGroup -> 0 = Cluster centers
    # flavClustGroup -> 1 = Dictionary containing clusters, key is the tuple of the clusters centers
    # catClustGroup -> tuple = Contains clusters centers and clusters of the category group
    # catClustGroup -> 0 = Cluster centers
    # catClustGroup -> 1 = Dictionary containing clusters, key is the tuple of the clusters centers
    # returns: list of restaurants in closest cluster to our identified flavor/user cluster
    def recommend(self, user):
        userFlavor = self.dp.createFlavorMatrix(user,self.cat[:,:-1])
        userFlavor = self.dp.attachId(userFlavor)
        # Find the closest flavor cluster
        rowFlavDistance = (self.find_clusters_distance_sorted_jacc(userFlavor[0], self.flavClusters[0]))[0]
        # # Find the category cluster thats closest to the flavor cluster
        flavCatDistance = (self.find_clusters_distance_sorted_jacc(rowFlavDistance[1], self.catClusters[0]))[0]
        # # Get the closest members to the user in a given cluster
        simRests = self.find_clusters_distance_sorted_jacc(userFlavor[0], self.catClusters[1][flavCatDistance[1]])
        simUsers = self.find_clusters_distance_sorted_jacc(userFlavor[0], self.flavClusters[1][rowFlavDistance[1]])


        
        newUtilIndices = []
        for u in simUsers:
            userIndex = int(u[1][len(u[1])-1])
            newUtilIndices.append(userIndex)
        newUtil = []
        for index in newUtilIndices:
            newUtil.append(self.utility[index])
        overallRatings = np.sum(newUtil,axis=0)
        ratedRestaurants = np.where(overallRatings>0)[0]

        newSimRests = []
        for r in simRests:
            restIndex = int(r[1][-1])
            if (user[0][restIndex] == 0) and (restIndex in ratedRestaurants):
                newSimRests.append(r)

        restRanking = np.flip(np.argsort(overallRatings))

        resVect = self.dp.getRestaurantKeys()

        client = MongoClient('127.0.0.1',port=27017)
        db = client["yelpData"]
        restNames = []
        finalRestIndices = []

        # This is the case where there are no intersection of restaurants b/w similar users and restaurant cluster, so we just stick to the restaurant cluster
        if len(newSimRests) == 0: 
            newSimRests = simRests


        businessIds = []

        for r in newSimRests:
            finalRestIndices.append(int(r[1][-1]))
            bus = db.businesses.find_one({ "business_id": resVect[str(int(r[1][-1]))]})
            restNames.append((bus["name"],bus["stars"],bus["address"]))
            businessIds.append(int(r[1][-1]))



        #Please let this be the last list of indices I ever see
        finalfinalRestIndicesFinal = []
        for i in finalRestIndices:
            finalfinalRestIndicesFinal.append(np.where(restRanking==i))

        rankedRestNames = [x for _,x in sorted(zip(finalfinalRestIndicesFinal,restNames))]
        
        if len(businessIds) > 100:
            rankedRestNames = rankedRestNames[0:99]
            businessIds = businessIds[0:99]
            
        return rankedRestNames,businessIds

    def find_clusters_distance_sorted_jacc(self, row, centroids):
        distanceList = []
        for center in centroids:
            distanceList.append([self.jaccardSim(row, center), tuple(center)])
        distanceList.sort(key=lambda x: x[0]) 
        return distanceList
        
    #x,y should be two arrays 
    #Returns: 1 - jaccard similarity of x and y 
    def jaccardSim(self,x,y):
        intersectSize = 0
        unionSize = 0

        for c,val in enumerate(x[:-1]):
            if val > 0:
                unionSize +=1
                if y[c] > 0:
                    intersectSize +=1

        for c,val in enumerate(y[:-1]):
            if val >0 and x[c] <= 0:
                unionSize +=1

        if unionSize == 0: #This is a person who has no taste and ruins our metrics. Shame on them
            return 1
        else:
            return 1-(intersectSize/unionSize)
        
    def evaluate(self):
        #crossValidation(utility, cat)
        pass

    def createFlavorAndAttachIds(self):
        #Create our flavorTown matrix
        self.flavorTown = self.dp.createFlavorMatrix(self.utility,self.cat)
        self.flavorTown = self.dp.attachId(self.flavorTown)
        self.cat = self.dp.attachId(self.cat)

        self.catClusters, self.flavClusters = hf.getClusters(self.cat,self.flavorTown)
     