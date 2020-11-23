import numpy as np
from model import Model
from DataProcessing import DataProcessing


dp = DataProcessing()
m = Model()

# get user matrix
testUser = dp.getUtilMatrix()
# get individual user in their own 2D array
testUser = np.asarray([testUser[7]])
# generate flavor profile
userFlavor = m.getUserFlavor(testUser)
# cluster on the model after generating user profile 
m.createClusters()
# run
print(m.recommend(userFlavor))
# print(testUser)
# print(userFlavor)
# print("BEFORE")
# print("number of user rows: ", len(testUser))
# print("number of user columns: ", len(testUser[0]))
# testUser = DataProcessing().attachId(testUser)
# # set individual user as 2D numpy array
# print("AFTER")

# print("number of user rows: ", len(testUser))
# print("number of user columns: ", len(testUser[0]))

# 
#print(m.recommend(testUser2))