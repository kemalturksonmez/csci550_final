# cscsi550_final

# Start up your mongo daemon
>$ mongod

# Enter mongo console
>$ mongo

# create mongo db
>\> use yelpData
>\> exit

# Import data into mongo
>$ mongoimport --db yelpData --collection businesses --type json --file ~/Desktop/yelp_dataset/yelp_academic_dataset_business.json 
>$ mongoimport --db yelpData --collection reviews --type json --file ~/Desktop/yelp_dataset/yelp_academic_dataset_review.json
>$ mongoimport --db yelpData --collection users --type json --file ~/Desktop/yelp_dataset/yelp_academic_dataset_user.json

# Start up mongo again
>$ mongo

# Delete all businesses that are not restaurants
>\> db.businesses.deleteMany({ categories: { $not: /Restaurants/ }})