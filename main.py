from pymongo import MongoClient
import numpy
import pandas as pd
client = MongoClient('127.0.0.1',port=27017)
db = client["yelpData"]

categories = dict()
reviews = list()
users = dict()
restaurants = dict()

businesses = db.businesses.find({ "city": "Montreal"}, no_cursor_timeout=True)

count = 0
num_businesses = 0
user_counter = 0
restaurant_counter = 0
for business in businesses:
    if restaurants.get(business["business_id"]) is None:
        restaurants[business["business_id"]] = restaurant_counter
        restaurant_counter += 1

    category_list = [x.strip() for x in business["categories"].split(',')]

    review_list = db.reviews.find({"business_id": business["business_id"]})
    for review in review_list:
        if users.get(review["user_id"]) is None:
            users[review["user_id"]] = user_counter
            user_counter += 1
        reviews.append((review["business_id"], review["user_id"], review["stars"]))

    num_businesses += 1
    for category in category_list:
        if categories.get(category) is None:           
            categories[category] = count
            count += 1

# rows, cols = df.shape

businesses = db.businesses.find({ "city": "Montreal"}, no_cursor_timeout=True)

cat_mat = numpy.zeros((count, num_businesses))

# print(cat_mat.shape)

for business in businesses:
    category_list = [x.strip() for x in business["categories"].split(',')]

    for category in category_list:
        cat_mat[categories[category]][restaurants[business["business_id"]]] = 1  

# for row in cat_mat:
#     print(row)
print(cat_mat)

print(user_counter)

util_mat = numpy.zeros((user_counter, num_businesses))

for review in reviews:
    bid = restaurants.get(review[0])
    uid = users.get(review[1])
    star = review[2]

    util_mat[uid][bid] = star

print(util_mat)

users_to_delete = list()

c = 0
reduced_util = list()
for user in util_mat:
    review_count = 0
    for r in user:
        if r > 0:
            review_count += 1
    
    if review_count > 5:
        reduced_util.append(user)
    

numpy.savetxt('cat_mat.txt', cat_mat, fmt="%d")
numpy.savetxt('util_mat.txt', reduced_util, fmt="%.2f")