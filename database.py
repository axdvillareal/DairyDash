import pymongo
myclient = pymongo.MongoClient("mongodb://localhost:27017/")
products_db = myclient["products"]
order_management_db = myclient["order_management"]

def get_product(code):
    products_coll = products_db["products"]

    product = products_coll.find_one({"code":code})

    return product

def get_products():
    product_list = []
    products_coll = products_db["products"]
    for p in products_coll.find({}):
        product_list.append(p)
    return product_list

def get_branch(code):
    branches_coll = order_management_db['branches']
    branch = branches_coll.find_one({"code":code})
    return branch

def get_branches():
    branch_coll = order_management_db['branches']
    branch_list = branch_coll.find({})
    return branch_list

# from previous entry we connected this to the order_management_db in MongoDB
def get_user(username):
    customers_coll = order_management_db['customers']
    user=customers_coll.find_one({"username":username})
    return user

def create_order(order):
    orders_coll = order_management_db['orders']
    orders_coll.insert(order)

def display_orders(username):
    print (username)
    orders_coll = order_management_db['orders']
    orderlist = orders_coll.find({'username':username})
    ordercount = orders_coll.count_documents({'username':username})
    return (orderlist, ordercount)

def changepassword(username, password):
    customers_coll = order_management_db['customers']
    customers_coll.update_one({"username":username},{"$set" : {"password":password}})
