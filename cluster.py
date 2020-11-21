import numpy as np
from sklearn.cluster import DBSCAN
class Cluster():
    def __init__(self):
        data = np.loadtxt("cat_mat.txt", delimiter=" ")
        self.numRest = len(data[0])
        self.cluster(data.T)
    
    def cluster(self, data):
        sklearn.cluster.DBSCAN(eps=0.5, min_samples=5, metric='euclidean').fit(data)
        
        
cluster = Cluster()