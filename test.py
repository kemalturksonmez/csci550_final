import numpy as np
from model import Model
from DataProcessing import DataProcessing
import time

dp = DataProcessing()
t = time.time()

# get user matrix
testUser = dp.getUtilMatrix()
# # get individual user in their own 2D array
testUser = np.asarray([testUser[10]])

print("Making model")
m = Model('Montreal')

print("recommending")
print(m.recommend(testUser))

elapsed = time.time() - t
print(elapsed)