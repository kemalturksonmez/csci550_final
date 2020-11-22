from pymongo import MongoClient
import numpy as np
import pandas as pd

from DataProcessing import DataProcessing
np.set_printoptions(threshold=np.inf)
d = DataProcessing()
# d.initialDataProcessing("Montreal")
# d.createMatrices()

utility = np.loadtxt("util_mat.txt", delimiter=" ",dtype=float)
cat = np.loadtxt("cat_mat.txt", delimiter=" ",dtype=float)

print(utility)
print(cat)

print(d.getFlavorTown(d.getNormalizedUtilMat(utility),cat))

