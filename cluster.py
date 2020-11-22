import numpy as np
from sklearn.cluster import DBSCAN
import numpy as np
from math import sqrt
from copy import deepcopy
import random
import matplotlib.pyplot as plt
class Cluster():
    def getClusterInfo(self, data):
        out = DBSCAN(eps=1.25, min_samples=2, metric='euclidean').fit(data)
        print(out.labels_)

    # gets the mean and standard deviations for each column in the dataset
    # data - dataset
    # returns: mean and dataset
    def mean_stdev(self, data):
        return np.mean(data, axis = 0), np.std(data, axis = 0)

    # calculates euclidean distance between two rows:
    # row - observed row
    # target - observed target row
    # returns: distance between given arrays
    def squared_euclidean_distance(self, row, target):
        distance = 0
        # doesn't get squared euc distance for final column
        # this is so we don't account for the class while comparing
        for i in range(len(row)-1):
            distance += (row[i]-target[i])**2
        return distance

    # organizes data set into appropriate clusters
    # data - dataset
    # centers - centroid/medoid set
    # returns: cluster dictionary
    def get_clusters(self, data, centers):
        # get clusters around medoids
        clusters = dict()
        for i in centers:
            clusters[tuple(i)] = list()
        for i in range(len(data)):
            tempDistance = []        
            for j in centers:
                # get list of distances
                tempDistance.append([self.squared_euclidean_distance(data[i], j), data[i], tuple(j)])
            # sorts based on distance 
            tempDistance.sort(key=lambda x: x[0]) 
            # append distance to appropriate
            clusters[tempDistance[0][2]].append(data[i])
        return clusters

    # gets squared euclidean distance between two old centroids and new centroids
    # new_centers - new centroids
    # old_centers - old centroids
    # returns:
    # distance - squared distance between new
    def get_difference(self, new_centers, old_centers):
        distance = 0
        for i in range(len(new_centers)):
            distance += self.squared_euclidean_distance(old_centers[i], new_centers[i])
        return distance

    # runs k - means for a given dataset
    # data - dataset
    # k - number of clusters
    # filename - name of dataset
    # returns: k centroids
    def get_centroids(self, data, k, minError):
        # # get mean and stdev
        mean, stdev = self.mean_stdev(data)
        # get number of features
        num_features = data.shape[1]
        # generate k random centers
        new_centers = np.random.random_sample((k,num_features))*stdev + mean
        old_centers = np.zeros(new_centers.shape)
        # graph
        # find the error between new and old cluster
        error = self.get_difference(new_centers,old_centers)
        while error > minError:
            # assign points to closest clusters
            clusters = self.get_clusters(data, new_centers)
            # copy new_distances to old_distances
            old_centers = deepcopy(new_centers)
            
            # init new array for centers
            new_centers = np.zeros(new_centers.shape)
            index = 0
            # temp dict for new cluster set
            temp = dict()
            # find mean of each cluster and create new centroids
            for i in clusters:
                clusterMean = i
                if len(clusters[i]) > 0:
                    # get mean
                    clusterMean, clusterStd = self.mean_stdev(clusters[i]) 
                # print() 
                # print(clusters[i]) 
                # print(clusterMean)  
                # print(tuple(clusterMean))
                temp[tuple(clusterMean)] = list()
                # get new center
                new_centers[index] = clusterMean
                index += 1
            clusters = temp
            error = self.get_difference(new_centers,old_centers)
        # round for classification
        clusters = self.get_clusters(data, new_centers)
        return new_centers, clusters

        
        
cluster = Cluster()
