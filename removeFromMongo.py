from pymongo import MongoClient
client = MongoClient('127.0.0.1',port=27017)
db = client["yelpData"]

print("Finding all businesses that aren't categorized as a restaurant")
# find all businesses that don't include the word restaurant
businesses = db.businesses.find({ "categories": { "$not": { "$regex": "Restaurants" } }}, no_cursor_timeout=True)
businessesCount = db.businesses.count_documents({ "categories": { "$not": { "$regex": "Restaurants" } }})
print("All businesses found")

print("Looking for reviews that are for businesses that aren't restaurants")
# iterate through and find all the reviews about businesses that aren't restaurants
count = 0
for business in businesses:
    # find reviews for business
    reviews = db.reviews.find({ "business_id": business["business_id"] })
    # delete reviews
    for review in reviews:
        db.reviews.delete_one({ "review_id": review["review_id"]})
        count += 1
    # delete business
    db.business.delete_one({"business_id": business["business_id"]})
print(count, " reviews deleted")
print(businessesCount, " reviews deleted")
businesses.close()

count = 0
# get document list of users
users = db.users.find({}, no_cursor_timeout=True)
for user in users:
    # get number of reviews a user has
    reviewCount = db.reviews.count_documents({ "user_id": user["user_id"]})
    # if the user has no reviews delete the user
    if reviewCount == 0:
        db.users.delete_one({"user_id": user["user_id"] })
        count += 1
users.close()
print(count, " reviews deleted")
# end connection
client.close()

