from pymongo import MongoClient
import numpy as np
import pandas as pd
import json
client = MongoClient('127.0.0.1',port=27017)
db = client["yelpData"]

class DataProcessing:
    def initialDataProcessing(self,city):
        #will contain categories as keys, unique index as value
        self.categories = dict()

        #will contain tuples of business_id, user_id, stars
        self.reviews = list()

        #Will contain user id as key, unique index as value
        self.users = dict()

        #Will contain busniess id as key, unique index as value
        self.restaurants = dict()

        #Get businesses from city
        businesses = db.businesses.find({ "city": city})


        #This loop populates most of the above variables
        count = 0
        user_counter = 0
        restaurant_counter = 0
        for business in businesses:     
            #populate categories
            category_list = [x.strip() for x in business["categories"].split(',')]
            if len(category_list) >= 3:
                for category in category_list:
                    if (self.categories.get(category) is None) and (category != 'Restaurants'):           
                        self.categories[category] = count
                        count += 1
                #Populate restaurants
                self.restaurants[business["business_id"]] = restaurant_counter
                restaurant_counter += 1

            review_list = db.reviews.find({"business_id": business["business_id"]})

            for review in review_list:
                if review["business_id"] in self.restaurants:
                    if self.users.get(review["user_id"]) is None:
                        self.users[review["user_id"]] = [1]
                    else:
                        self.users[review["user_id"]][0] += 1 
                    self.users[review["user_id"]].append((review["business_id"], review["user_id"], review["stars"]))
                    #self.reviews.append((review["business_id"], review["user_id"], review["stars"]))

            review_list.close()     
        
        businesses.close()

        newUsers = dict()
        for user,value in self.users.items():
            if value[0] < 5:
                pass
            else:
                for review in range(1,len(value)):
                    self.reviews.append(value[review])

                newUsers[user] = user_counter
                user_counter += 1
        self.users = newUsers
        
        self.writeSwappedKeys(self.users, 'users.json')
        self.writeSwappedKeys(self.restaurants, 'businesses.json')

        return self.users, self.restaurants

    def createMatrices(self):
        
        businesses = db.businesses.find({ "city": "Montreal"})

        #create category matrix of size # categories x # businesses
        # self.cat_mat = np.zeros((len(self.categories), len(self.restaurants)))
        self.cat_mat = np.zeros((len(self.restaurants), len(self.categories)))

        #Populate category matrix
        for business in businesses:
            if business["business_id"] in self.restaurants:
                category_list = [x.strip() for x in business["categories"].split(',')]
                for category in category_list:
                    if category != 'Restaurants':
                        #For each category, set the value where the category row and business column intersect.
                        # self.cat_mat[self.categories[category]][self.restaurants[business["business_id"]]] = 1
                        self.cat_mat[self.restaurants[business["business_id"]]][self.categories[category]] = 1   

        #Create utility matrix of size #customers x # businesses
        self.util_mat = np.zeros((len(self.users), len(self.restaurants)))

        #Populate utility matrix
        for review in self.reviews:
            bid = self.restaurants.get(review[0])
            uid = self.users.get(review[1])
            star = review[2]

            self.util_mat[uid][bid] = star

        np.savetxt('cat_mat.txt', self.cat_mat, fmt="%.2f")
        np.savetxt('util_mat.txt', self.util_mat, fmt="%.2f")

        return self.cat_mat, self.util_mat

    #return normalized flavor town (or single user if user's row in utility matrix is passed in as utilMatrix)
    def getFlavorTown(self,utilMatrix,categoryMatrix):
        # flavorTown = np.matmul(utilMatrix,categoryMatrix.T)
        flavorTown = np.matmul(utilMatrix,categoryMatrix)
        
        for rowNum,row in enumerate(flavorTown):
            rowMax = np.max(abs(row))
            for colNum,value in enumerate(row):
                if value!=0:
                    flavorTown[rowNum][colNum] = float(value) / float(rowMax)
        
        return flavorTown

    #Get normalized util matrix
    def getNormalizedUtilMat(self,utilMatrix):
        norm_util = np.zeros(utilMatrix.shape)

        #Bit of black magic to get average stars per user
        avgStars = np.true_divide(utilMatrix.sum(1),(utilMatrix!=0).sum(1))
        for userNum,user in enumerate(utilMatrix):
            for revNum,review in enumerate(user):
                if review != 0:
                    norm_util[userNum][revNum] = float(review) - avgStars[userNum] + 1
                revNum += 1

            userNum += 1

        return norm_util
    
    def createFlavorMatrix(self, utility, cat):
        return self.getFlavorTown(self.getNormalizedUtilMat(utility),cat)

    def writeSwappedKeys(self, keyDict, fileName):
        tempDict = dict()
        for key,val in keyDict.items():
            tempDict[val] = key
        with open(fileName, 'w+') as outfile:
            json.dump(tempDict, outfile, indent=2)

    def writeFlavorMatrix(self, flavorTown):
        np.savetxt('flavor_town_mat.txt', flavorTown, fmt="%.2f")
        
    def getCatMatrix(self):
        return np.loadtxt("cat_mat.txt", delimiter=" ",dtype=float)
    
    def getUtilMatrix(self):
        return np.loadtxt("util_mat.txt", delimiter=" ",dtype=float)

    def getUserKeys(self):
        with open('users.json') as json_file:
            data = json.load(json_file)
        return data
    
    def getRestaurantKeys(self):
        with open('businesses.json') as json_file:
                data = json.load(json_file)
        return data
    
    def getFlavorMatrix(self):
        return np.loadtxt("flavor_town_mat.txt", delimiter=" ",dtype=float) 
    
    def getAllFiles(self):
        users = self.getUserKeys()
        restaurants = self.getRestaurantKeys()
        cat = self.getCatMatrix()
        utility = self.getUtilMatrix()
        flavorMatrix = self.getFlavorMatrix()
        return users, restaurants, cat, utility, flavorMatrix

    def attachId(self, matrix):
        newMatrix = np.zeros((matrix.shape[0], matrix.shape[1] + 1))
        for rowIndex in range(len(matrix)):
            newMatrix[rowIndex] = np.append(matrix[rowIndex],rowIndex)
        return newMatrix
