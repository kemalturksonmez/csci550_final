from pymongo import MongoClient
import numpy as np
import pandas as pd
from DataProcessing import DataProcessing
from cluster import Cluster
np.set_printoptions(threshold=np.inf)

def createInfo(cityName):
    d = DataProcessing()

    users, restaurants = d.initialDataProcessing(cityName)
    cat, utility = d.createMatrices()

    # utility = d.getUtilMatrix()
    # cat = d.getCatMatrix()

    # print(utility)
    # print(cat)

    flavorTown = d.getFlavorTown(d.getNormalizedUtilMat(utility),cat)
    return users, restaurants, cat, utility, flavorTown

def getClusters(cat, flavorTown):
    flavorTown = DataProcessing().attachId(flavorTown)
    cat = DataProcessing().attachId(cat)
    flavor_centers, flavor_clusters = Cluster().get_centroids(flavorTown, 7, 0.001)
    cat_centers, cat_clusters = Cluster().get_centroids(cat, 7, 0.001)
    


# users, restaurants, cat, utility, flavorTown = createInfo("Montreal")
users, restaurants, cat, utility, flavorTown = DataProcessing().getAllFiles()
getClusters(cat, flavorTown)
