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
            self.users, self.restaurants, self.cat, self.utility = self.dp.getAllFiles()
            self.createFlavorAndAttachIds()
        elif type(city) == type('string'):
            self.users, self.restaurants = self.dp.initialDataProcessing(city)
            self.cat, self.utility = self.dp.createMatrices()
            self.createFlavorAndAttachIds()
        else:
            self.users = city[0]
            self.restaurants = city[1]
            self.cat = city[2]
            self.utility = city[3]
            self.flavorTown = city[4]



        #Get clusters for restaurants and users
        self.catClusters, self.flavClusters = hf.getClusters(self.cat,self.flavorTown)

    # flavClustGroup -> tuple = Contains clusters centers and clusters of the flavor group
    # flavClustGroup -> 0 = Cluster centers
    # flavClustGroup -> 1 = Dictionary containing clusters, key is the tuple of the clusters centers
    # catClustGroup -> tuple = Contains clusters centers and clusters of the category group
    # catClustGroup -> 0 = Cluster centers
    # catClustGroup -> 1 = Dictionary containing clusters, key is the tuple of the clusters centers
    # returns: list of restaurants in closest cluster to our identified flavor/user cluster
    def recommend(self,user):
        #get the user's flavor vector
        userFlavor = self.dp.createFlavorMatrix(user,self.cat)
        # Find the closest flavor cluster
        rowFlavDistance = (self.cluster.find_clusters_distance_sorted(userFlavor, self.flavClusters[0]))[0]
        # # Find the category cluster thats closest to the flavor cluster
        flavCatDistance = (self.cluster.find_clusters_distance_sorted(rowFlavDistance[1], self.catClusters[0]))[0]
        # # Get the closest members to the user in a given cluster
        simRests = self.cluster.find_clusters_distance_sorted(userFlavor, self.catClusters[1][flavCatDistance[1]])
        restNames = []
        #print(simRests)

        resVect = self.dp.getRestaurantKeys()
        #print(resVect)
        client = MongoClient('127.0.0.1',port=27017)
        db = client["yelpData"]
        for r in simRests:
            #print(r)
            # print()
            bus = db.businesses.find_one({ "business_id": resVect[str(int(r[1][-1]))]})
            restNames.append((bus["name"],bus["stars"],bus["address"]))

        #rank restaurants?

        return restNames



    def evaluate(self):
        #crossValidation(utility, cat)
        pass

    def createFlavorAndAttachIds(self):
        #Create our flavorTown matrix
        self.flavorTown = self.dp.createFlavorMatrix(self.utility,self.cat)
        self.flavorTown = self.dp.attachId(self.flavorTown)
        self.cat = self.dp.attachId(self.cat)
     



