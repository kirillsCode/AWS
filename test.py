import boto3
#import httplib
#import urllib
import datetime
#from datetime import date
from collections import defaultdict

region = 'us-west-2'
ec2=boto3.resource('ec2', region_name = region)
dns = ['ec2-54-70-209-171.us-west-2.compute.amazonaws.com', 'ec2-34-217-218-93.us-west-2.compute.amazonaws.com', 'ec2-54-70-215-226.us-west-2.compute.amazonaws.com','ec2-52-33-204-20.us-west-2.compute.amazonaws.com']
my_instances = ec2.instances.filter(Filters=[{'Name':'dns-name','Values':dns}])

for inst in my_instances:
    instancename = ''
    for tag in inst.tags:
        if tag["Key"] == 'Name':
            instancename = tag["Value"]
    #print instancename,'  ----  ',inst.state['Name']
    if int(inst.state['Code']) == 80:
        nowtime = datetime.datetime.now().strftime('%Y-%m-%d')
        try:
            ami = inst.create_image(
                Description = instancename + "   " + nowtime,
                Name = "ami_" + instancename
            )
        except Exception, e:
            print "Failed to create image ", e
        inst.terminate()

#print boto3.session.Session().get_available_regions('ec2')
# for another availability zone I'd get another ec2 resource with another region_name       
images = ec2.images.filter(Owners=["self"])
today = datetime.datetime.today()
for im in images:
    created_date = datetime.datetime.strptime(im.creation_date, '%Y-%m-%dT%H:%M:%S.000Z')
    #print created_date
    #print today
    im_time = abs(created_date - today)
    #print im_time.days
    if im_time.days > 7:
        im.deregister(delete_snapshot = True)

inst_attr = defaultdict()
for inst in ec2.instances.all():
    instname = ''
    if inst.tags:
        for tag in inst.tags:
            if tag["Key"] == 'Name':
                instname = tag["Value"]
    inst_attr[inst.id] = {'Name': instname,'State': inst.state['Name'],'Public_ip': inst.public_ip_address}

attr = ['Name','State','Public_ip']
for inst_id, attrib in inst_attr.items():
    print ("{}".format(inst_id))
    for key in attr:
        print("{:>20}: {}".format(key, attrib[key]))
    print("-----------------")

#conn=httplib.HTTPConnection("scientia.pp.ua")
#conn.request("HEAD", "/")
#resp=conn.getresponse()
#print resp.status, resp.reason
	
#print urllib.urlopen("http://scientia.pp.ua").getcode()

