from pymongo import MongoClient
import numpy as np
import pandas as pd

from DataProcessing import DataProcessing

d = DataProcessing("Montreal")
d.createMatrices()

print(d.getFlavorTown())
print(d.getNormalizedUtilMat())
print(d.util_mat)