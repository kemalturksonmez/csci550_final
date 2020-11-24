import numpy as np
from model import Model
from DataProcessing import DataProcessing

dp = DataProcessing()


# get user matrix
testUser = dp.getUtilMatrix()
# # get individual user in their own 2D array
testUser = np.asarray([testUser[7]])


# # run
m = Model()
print(m.recommend(testUser))
