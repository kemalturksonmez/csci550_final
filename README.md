# cscsi550_final

# Start up your mongo daemon
<p><code>$ mongod</p></code>

# Enter mongo console
<p><code>$ mongo</p></code>

# create mongo db
<p><code>> use yelpData </p></code>
<p><code>> exit</p></code>

# Import data into mongo
<p><code>$ mongoimport --db yelpData --collection businesses --type json --file ~/Desktop/yelp_dataset/yelp_academic_dataset_business.json</p></code>
<p><code>$ mongoimport --db yelpData --collection reviews --type json --file ~/Desktop/yelp_dataset/yelp_academic_dataset_review.json</p></code>
<p><code>$ mongoimport --db yelpData --collection users --type json --file ~/Desktop/yelp_dataset/yelp_academic_dataset_user.json</p></code>

# Start up mongo again
<p><code>$ mongo</p></code>
<p><code>> use yelpData </p></code>

# Delete all reviews that belong to businesses that are not restaurants
<p><code>> db.reviews.deleteMany({ business_id: {$in: db.businesses.distinct("business_id", { categories: { $not: /Restaurants/ }}) } })</p></code>

# Delete all businesses that are not restaurants
<p><code>> db.businesses.deleteMany({ categories: { $not: /Restaurants/ }})</p></code>

# Aggregate reviews and group by user id
<p><code>db.reviews.aggregate([{"$group" : {_id:"$user_id"}}], {allowDiskUse:true}).map(function(el) { return el._id })</code></p>

# Install pymongo if you don't have it
<p><code>$ pip3 install pymongo</p></code>
 
