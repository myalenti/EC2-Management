import string
import logging
import pymongo
from pymongo import MongoClient, InsertOne
import boto3
import re

logging.basicConfig(level=logging.INFO,
                    format='(%(threadName)4s) %(levelname)s %(message)s',
                    )

def dbLoader(request,tgtCol):
    connection = MongoClient(target,port)
    #connection.admin.authenticate(username,password)
    db = connection.amazon
    collection = db[tgtCol]
    bulk_result = collection.bulk_write(request)
    logging.info("Starting bulk load results %s" % (bulk_result.bulk_api_result))
    


def loadInstances():
    instances = dict()

    for i in regions["Regions"]:
        r = i["RegionName"]
        logging.info("Finding instances for %s" % r )
        #print "Finding instances for " + r
        client = boto3.client('ec2',region_name=r)
        instances.update(client.describe_instances())
        instCount = len(instances["Reservations"])
    
        if instCount == 0:
            logging.info("Instance count is 0 - skipping" )
            #print "Instance count is 0 - skipping"
        else:
            logging.info("Instance count is %d - skipping" % instCount )
            #print "Instance count is " + str(instCount)
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
    logging.info("%d users loaded" % len(users["Users"]) )
    #print "Loading " + str(len(users["Users"])) + "users"
    dbLoader(request,"iam")
    
def loadVolumes():
    volumes = dict()
    
    for i in regions["Regions"]:
        r = i["RegionName"]
        logging.info("Finding Volumes for %s" % r )
        client = boto3.client("ec2",region_name=r)
        volumes = client.describe_volumes()
        volCount = len(volumes["Volumes"])
        
        if volCount == 0:
            logging.info("Volume count is 0 - skipping")
        else:
            request = []
            for i in volumes["Volumes"]:
                request.append(InsertOne(i))
            logging.info("%d Volumes loaded" % len(volumes["Volumes"]) )
            dbLoader(request,"volumes")
    
def loadSnapshots():
    snapshots = dict()
    
    for i in regions["Regions"]:
        r = i["RegionName"]
        logging.info("Finding Snapshots for %s" % r)
        client = boto3.client("ec2",region_name=r)
        snapshots = client.describe_snapshots()
        snapCount = len(snapshots["Snapshots"])
        
        if snapCount == 0:
            logging.info("Snapshot Count is 0 - skipping")
        else:   
            request = []
            for i in snapshots["Snapshots"]:
                request.append(InsertOne(i))
            logging.info("%d Snapshots loaded" % len(snapshots["Snapshots"]) )
            dbLoader(request,"snapshots")

def findEx():
    connection = MongoClient(target,port)
    #connection.admin.authenticate(username,password)
    db = connection.amazon
    terminations = db["terminations"].find({})
    print "Currently searching for this number of old employees: " + str(terminations.count())
    for i in terminations:
        username=i["First Name"]+"."+i["Last Name"]
        #print username
        user_cursor = db.iam.find( { "UserName" : { '$regex' : username, '$options' : 'i'}})
        if user_cursor.count() != 0:
            print "Old user found " + i["First Name"] + " " + i["Last Name"]
    
#    logging.info("Starting bulk load results %s" % (bulk_result.bulk_api_result))
    
    
#Global Variables
target = "localhost"
port = 27017
#client = boto3.client('ec2',region_name=None)
#regions = client.describe_regions()  

#loadUsers()
#loadInstances()
#loadVolumes()
#loadSnapshots()
findEx()