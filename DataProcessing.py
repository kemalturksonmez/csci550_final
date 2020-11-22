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

            #Populate restaurants
            if self.restaurants.get(business["business_id"]) is None:
                self.restaurants[business["business_id"]] = restaurant_counter
                restaurant_counter += 1

            review_list = db.reviews.find({"business_id": business["business_id"]})

            for review in review_list:
                if self.users.get(review["user_id"]) is None:
                    self.users[review["user_id"]] = [1]
                else:
                    self.users[review["user_id"]][0] += 1 
                self.users[review["user_id"]].append((review["business_id"], review["user_id"], review["stars"]))
                #self.reviews.append((review["business_id"], review["user_id"], review["stars"]))

            review_list.close()


            #populate categories
            category_list = [x.strip() for x in business["categories"].split(',')]
            for category in category_list:
                if (self.categories.get(category) is None) and (category != 'Restaurants'):           
                    self.categories[category] = count
                    count += 1
        
        businesses.close()

        newUsers = dict()
        for user,value in self.users.items():
            if value[0] < 3:
                pass
            else:
                for review in range(1,len(value)):
                    self.reviews.append(value[review])

                newUsers[user] = user_counter
                user_counter += 1
        self.users = newUsers
        
        self.writeSwappedKeys(self.users, 'users.json')
        self.writeSwappedKeys(self.restaurants, 'businesses.json')
        # # write user keys to file
        # with open('users.json', 'w+') as outfile:
        #     json.dump(self.users, outfile, indent=2)
        # # write restaurant keys to file
        # with open('businesses.json', 'w+') as outfile:
        #     json.dump(self.restaurants, outfile, indent=2)
        return self.users, self.restaurants

    def createMatrices(self):
        
        businesses = db.businesses.find({ "city": "Montreal"})

        #create category matrix of size # categories x # businesses
        # self.cat_mat = np.zeros((len(self.categories), len(self.restaurants)))
        self.cat_mat = np.zeros((len(self.restaurants), len(self.categories)))

        #Populate category matrix
        for business in businesses:
            category_list = [x.strip() for x in business["categories"].split(',')]

            for category in category_list:
                if category != 'Restaurants':
                    #For each category, set the value where the category row and business column intersect.
                    # self.cat_mat[self.categories[category]][self.restaurants[business["business_id"]]] = 1
                    self.cat_mat[self.restaurants[business["business_id"]]][self.categories[category]] = 1   

        # for row in cat_mat:
        #     print(row)
        #print(self.cat_mat)

        #print(user_counter)

        #Create utility matrix of size #customers x # businesses
        self.util_mat = np.zeros((len(self.users), len(self.restaurants)))

        #Populate utility matrix
        for review in self.reviews:
            bid = self.restaurants.get(review[0])
            uid = self.users.get(review[1])
            star = review[2]

            self.util_mat[uid][bid] = star

        

        #Remove users with less than 5 reviews.
        # might not need?
        # c = 0
        # reduced_util = list()
        # for user in self.util_mat:
        #     review_count = 0
        #     for r in user:
        #         if r > 0:
        #             review_count += 1
            
        #     if review_count >= 5:
        #         reduced_util.append(user)
        # self.util_mat = reduced_util

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
        np.savetxt('flavor_town_mat.txt', flavorTown, fmt="%.2f")
        return flavorTown

    #Get normalized util matrix
    def getNormalizedUtilMat(self,utilMatrix):
        norm_util = np.zeros(utilMatrix.shape)

        #Bit of black magic to get average stars per user
        avgStars = np.true_divide(utilMatrix.sum(1),(utilMatrix!=0).sum(1))
        for userNum,user in enumerate(utilMatrix):
            for revNum,review in enumerate(user):
                if review != 0:
                    norm_util[userNum][revNum] = float(review) - avgStars[userNum]
                revNum += 1

            userNum += 1

        return norm_util
    
    def writeSwappedKeys(self, keyDict, fileName):
        tempDict = dict()
        for key,val in keyDict.items():
            tempDict[val] = key
        with open(fileName, 'w+') as outfile:
            json.dump(tempDict, outfile, indent=2)
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
        flavorTown = self.getFlavorMatrix()
        return users, restaurants, cat, utility, flavorTown

    def attachId(self, matrix):
        newMatrix = np.zeros((matrix.shape[0], matrix.shape[1] + 1))
        for rowIndex in range(len(matrix)):
            newMatrix[rowIndex] = np.append(matrix[rowIndex],rowIndex)
        return newMatrix
