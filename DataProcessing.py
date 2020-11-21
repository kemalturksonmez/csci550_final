from pymongo import MongoClient
import numpy as np
import pandas as pd

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

        
            #Populate reviews
            review_list = db.reviews.find({"business_id": business["business_id"]})
            for review in review_list:
                if self.users.get(review["user_id"]) is None:
                    self.users[review["user_id"]] = user_counter
                    user_counter += 1
                self.reviews.append((review["business_id"], review["user_id"], review["stars"]))

            #populate categories
            category_list = [x.strip() for x in business["categories"].split(',')]
            for category in category_list:
                if (self.categories.get(category) is None) and (category != 'Restaurants'):           
                    self.categories[category] = count
                    count += 1
        
        businesses.close()

    def createMatrices(self):
        
        businesses = db.businesses.find({ "city": "Montreal"})

        #create category matrix of size # categories x # businesses
        self.cat_mat = np.zeros((len(self.categories), len(self.restaurants)))

        #Populate category matrix
        for business in businesses:
            category_list = [x.strip() for x in business["categories"].split(',')]

            for category in category_list:
                if category != 'Restaurants':
                    #For each category, set the value where the category row and business column intersect.
                    self.cat_mat[self.categories[category]][self.restaurants[business["business_id"]]] = 1  

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
        
        businesses.close()

        np.savetxt('cat_mat.txt', self.cat_mat, fmt="%.2f")
        np.savetxt('util_mat.txt', self.util_mat, fmt="%.2f")

        return self.cat_mat, self.util_mat

    #return normalized flavor town (or single user if user's row in utility matrix is passed in as utilMatrix)
    def getFlavorTown(self,utilMatrix,categoryMatrix):
        flavorTown = np.matmul(utilMatrix,categoryMatrix.T)
        
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
                    norm_util[userNum][revNum] = float(review) - avgStars[userNum]
                revNum += 1

            userNum += 1

        return norm_util
        
