import string
import logging
import boto3
import json
import datetime
import time
import getopt, sys
import re

logging.basicConfig(level=logging.INFO,
                    format='(%(threadName)4s) %(levelname)s %(message)s',
                    )

def usage():
    print "EC2 Management usage"
    print "     -r overrides list of regions from default of us-east-1 to all"
    print "     -s <action> action to apply to instances (stop or start are only valid values)"
    print "     -t causing retagging to take place"
    print "     -h causes this help to be displayed"
    print "     --level <DEBUG,INFO,WARNING>"
    
tag=False
state="none"
pattern="myalenti*"
regions = { "Regions" : [{ "RegionName" : "us-east-1"}]}
client = boto3.client('ec2',region_name=None)
    
try:
    opts, args = getopt.getopt(sys.argv[1:], "rts:", ["level="])
    logging.debug("Operation list length is : %d " % len(opts))
except getopt.GetoptError:
    print "You provided invalid command line switches."
    usage()
    exit(2)

    
for opt, arg in opts:
    #print "Tuple is " , opt, arg
    if opt in ("-t"):
        print "Setting Tag Instances to True"
        tag=True
    elif opt in ("-r"):
        print "Setting regions to all regions"
        regions = client.describe_regions()  
    elif opt in ("-s"):
        print "Applying State action of: ", arg
        state = str(arg)
    elif opt in ("--level"):
        print "Log Level set to : ", arg
        arg = arg.upper() 
        if not arg in ("DEBUG", "WARN", "INFO"):
            print "Invalid logging level specified - choices are DEBUG WARN INFO"
            exit(2)
        else:
            logging.getLogger().setLevel(arg)
    elif opt in ("-h"):
        print "Generating help info"
        usage()
        exit()
    else:
        print "Invalid Prameters detected"
        usage()
        exit(2)    


def loadInstances():
    #instances = dict()
    instances = {}

    for i in regions["Regions"]:
        r = i["RegionName"]
        logging.info("Finding instances for %s" % r )
        client = boto3.client('ec2',region_name=r)
        try: 
            instances.update(client.describe_instances(Filters=[{ 'Name' : 'tag:Name', 'Values' : [ pattern ]}]))
        except:
            continue
        
        instCount = len(instances["Reservations"])
        logging.info("Total instances matching pattern %s was %d" % (pattern, instCount))
        if instCount == 0:
            logging.info("Instance count is 0 - no systems with tag name matching pattern" )
        else:
            for n in instances["Reservations"]:
                instanceId=n["Instances"][0]["InstanceId"]
                for m in n["Instances"][0]["Tags"]:
                    if m["Key"] == "Name":
                      instanceName=m["Value"]
                      
                print instanceId + " " + instanceName
                if tag == True:
                    logging.debug("Preparing to execute setTags")
                    if  re.match('myalenti-ld.*',instanceName):
                        print "Matched a loader"
                        setTags(r,instanceId,instanceName,"load")
                    elif re.match('myalenti-rpl.*',instanceName):
                        print "Matched a demo system"
                        setTags(r,instanceId,instanceName,"demo")
                    elif re.match('myalenti-tst.*',instanceName):
                        print "Matched a misc system"
                        setTags(r,instanceId,instanceName,"misc")
                    elif re.match('myalenti-agt.*',instanceName):
                        print "Matched a agent system"
                        setTags(r,instanceId,instanceName,"agent")
                    else:
                        print "No specific match made"
                        setTags(r,instanceId,instanceName,"none")
                else:
                    logging.debug("Retagging not taking place")
                    
                    #setTags(r,instanceId,instanceName)
                
def setTags(region,instanceID,instanceName,instType):
    futureDate = datetime.datetime.now() + datetime.timedelta(days=30)
    stringDate = datetime.datetime.strftime(futureDate, "%Y-%m-%d")
    ownerStr = "mark.yalenti"
    owner = { "Key" : "owner", "Value" : ownerStr }
    prj_demo = { "Key" : "project", "Value" : "demo" }
    prj_load = { "Key" : "project" , "Value" : "loader"}
    prj_misc = { "Key" : "project" , "Value" : "misc"}
    prj_agent = { "Key" : "project" , "Value" : "agent"}
    expire_on = { "Key" : "expire-on" , "Value" : stringDate } 
    
    client = boto3.resource('ec2', region_name=region)
    instance = client.Instance(instanceID)
    
    if instType == "load":
        logging.info("Applying Updated tags, expiration date %s, owner %s , project loader to instance %s" % ( stringDate, ownerStr, instanceName))
        tags = instance.create_tags( Tags=[owner,expire_on,prj_load])
    elif instType == "demo":
        logging.info("Applying Updated tags, expiration date %s, owner %s , project demo to instance %s" % ( stringDate, ownerStr, instanceName))
        tags = instance.create_tags( Tags=[owner,expire_on,prj_demo])
    elif instType == "agent":
        logging.info("Applying Updated tags, expiration date %s, owner %s , project agent to instance %s" % ( stringDate, ownerStr, instanceName))
        tags = instance.create_tags( Tags=[owner,expire_on,prj_agent])
    elif instType == "misc":
        logging.info("Applying Updated tags, expiration date %s, owner %s , project misc to instance %s" % ( stringDate, ownerStr, instanceName))
        tags = instance.create_tags( Tags=[owner,expire_on,prj_misc])
    else:
        logging.info("Applying Updated tags, expiration date %s, owner %s to instance %s" % ( stringDate, ownerStr, instanceName))
        tags = instance.create_tags( Tags=[owner,expire_on])
       

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
    

#Global Variables

loadInstances()
#loadVolumes()
