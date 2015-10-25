import string
import pymongo
from pymongo import MongoClient, InsertOne
import boto3

def dbLoader(request,tgtCol):
    connection = MongoClient(target,port)
    #connection.admin.authenticate(username,password)
    db = connection.amazon
    collection = db[tgtCol]
    bulk_result = collection.bulk_write(request)
    print bulk_result.bulk_api_result

target = "localhost"
port = 27017


def loadInstances():
    client = boto3.client('ec2',region_name=None)
    regions = client.describe_regions()
    instances = dict()

    for i in regions["Regions"]:
        r = i["RegionName"]
        print "Finding instances for " + r
        client = boto3.client('ec2',region_name=r)
        instances.update(client.describe_instances())
        instCount = len(instances["Reservations"])
    
        if instCount == 0:
            print "Instance count is 0 - skipping"
        else:
            print "Instance count is " + str(instCount)
            request = []
            for i in instances["Reservations"]:
                request.append(InsertOne(i))
            dbLoader(request,"ec2")
            
def loadUsers():
    users = dict()
    client = boto3.client("iam")
    users = client.list_users()
    request = []
    
    for i in users["Users"]:
        request.append(InsertOne(i))
    print "Loading " + str(len(users["Users"])) + "users"
    dbLoader(request,"iam")
    

loadUsers()
loadInstances()