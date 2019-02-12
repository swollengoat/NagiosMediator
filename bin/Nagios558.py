#!/usr/bin/python

##############################
#
# Nagios 5.5.8 mediator for IBM Predictive Insights
#
# 1/29/19 - Jason Cress (jcress@us.ibm.com)
#
###################################################

import urllib2
import json
import sys
import time
import re
import datetime
import os

#################
#
#  Initial configuration items
#
##############################

if(os.path.isdir("../nagioscsv")):
   csvFileDir = "../nagioscsv/"
else:
   csvFileDir = "./"

myTimeStamp = time.strftime("%Y%m%d%H%M%S", time.gmtime())
myProtocol = "http"
myNagiosHost = "192.168.2.127"
myNagiosPort = "80"
myApiKey = "ucMCdER6V46mf5HTbSufj73QJVVCN4HBfpaLk08fkdUChBrLpfZLGjSlu4dh8TRG"

serviceStatusQuery = myProtocol + "://" + myNagiosHost + ":" + myNagiosPort + "/nagiosxi/api/v1/objects/servicestatus?apikey=" + myApiKey + "&pretty=1"

hostStatusQuery = myProtocol + "://" + myNagiosHost + ":" + myNagiosPort + "/nagiosxi/api/v1/objects/hoststatus?apikey=" + myApiKey + "&pretty=1"

############################
#
#  Perform hoststatus and servicehosts API queries and parse json responses as python objects
#
#############################################################################################

hostStatusContents = urllib2.urlopen(hostStatusQuery).read()
serviceStatusContents = urllib2.urlopen(serviceStatusQuery).read()

hostStatusApiOutput = open("hostStatusApiOutput.json", "w")
hostStatusApiOutput.write(hostStatusContents)
hostStatusApiOutput.close

serviceStatusApiOutput = open("serviceStatusApiOutput.json", "w")
serviceStatusApiOutput.write(serviceStatusContents)
serviceStatusApiOutput.close

parsedHostStatusContents = json.loads(hostStatusContents)
parsedServiceStatusContents = json.loads(serviceStatusContents)

############################
#
# Iterate through records and build hostStatus and pingData csv files
#
#####################################################################

# open files for writing

hostStatusCsvFile = open(csvFileDir + "hostStatus" + str(myTimeStamp) + ".csv", "a")
hostStatusCsvFile.write("\"timestamp\",\"name\",\"rta\",\"pl\"\n")
pingDataCsvFile = open(csvFileDir + "pingData" + str(myTimeStamp) + ".csv", "a")
pingDataCsvFile.write("\"timestamp\",\"host name\",\"ping_rta value\",\"ping_pl value\"\n")
cpuStatsCsvFile = open(csvFileDir + "cpuStats" + str(myTimeStamp) + ".csv", "a")
cpuStatsCsvFile.write("\"timestamp\",\"host name\",\"user\",\"system\",\"io wait\",\"idle\"\n")
totalProcessCsvFile = open(csvFileDir + "totalProcess" + str(myTimeStamp) + ".csv", "a")
totalProcessCsvFile.write("\"timestamp\",\"host name\",\"total processes\"\n")
swapUsageCsvFile = open(csvFileDir + "swapUsage" + str(myTimeStamp) + ".csv", "a")
swapUsageCsvFile.write("\"timestamp\",\"host name\",\"swap data\"\n")
cpuUsageCsvFile = open(csvFileDir + "cpuUsage" + str(myTimeStamp) + ".csv", "a")
cpuUsageCsvFile.write("\"timestamp\",\"host name\",\"cpu usage\"\n")
memoryDataCsvFile = open(csvFileDir + "memoryData" + str(myTimeStamp) + ".csv", "a")
memoryDataCsvFile.write("\"timestamp\",\"host name\",\"memory total \",\"memory used\"\n")
usersCsvFile = open(csvFileDir + "users" + str(myTimeStamp) + ".csv", "a")
usersCsvFile.write("\"timestamp\",\"host name\",\"user\"\n")
memoryUsageCsvFile = open(csvFileDir + "memoryUsage" + str(myTimeStamp) + ".csv", "a")
memoryUsageCsvFile.write("\"timestamp\",\"host name\",\"committed\",\"physical\"\n")
diskUsageCsvFile = open(csvFileDir + "diskUsage" + str(myTimeStamp) + ".csv", "a")
diskUsageCsvFile.write("\"timestamp\",\"host name\",\"disk name\",\"disk used\"\n")
currentLoadCsvFile = open(csvFileDir + "currentLoad" + str(myTimeStamp) + ".csv", "a")
currentLoadCsvFile.write("\"timestamp\",\"host name\",\"Load5\"\n")

recordCount = int(parsedHostStatusContents['recordcount'])
print("number of host records: " + str(recordCount))

recordIndex = 0
while recordIndex < recordCount:
   print("hostname: " + parsedHostStatusContents['hoststatus'][recordIndex]['name'])
   hostName = parsedHostStatusContents['hoststatus'][recordIndex]['name']
   # extract rta for server
   extr = re.search('rta=(.+?)ms', parsedHostStatusContents['hoststatus'][recordIndex]['performance_data']) 
   if extr:
      rta = extr.group(1)
   else:
      rta = 0
   # extract packet loss for server
   extr = re.search('pl=(.+?)\%', parsedHostStatusContents['hoststatus'][recordIndex]['performance_data'])
   if extr:
      pl = extr.group(1)
   else:
      pl = 0
   # build the data string and write to file
   hostStatusDataString = str(myTimeStamp) + "," + hostName + "," + str(rta) + "," + str(pl) 
   #print(hostStatusDataString)

   # Write the pingData and hostStatus files
   pingDataCsvFile.write(hostStatusDataString + "\n")
   hostStatusCsvFile.write(hostStatusDataString + "\n")

   # grab swap usage for this host from the service data
   recordIndex = recordIndex + 1

###########
#
#  Iterate through service status response and pull PI metrics of interest, write to files
#
##########################################################################################

recordCount = int(parsedServiceStatusContents['recordcount'])
print("number of service status records: " + str(recordCount))

recordIndex = 0
while recordIndex < recordCount:

   myHostName = parsedServiceStatusContents['servicestatus'][recordIndex]['host_name']
   myServiceName = parsedServiceStatusContents['servicestatus'][recordIndex]['name']

   if(parsedServiceStatusContents['servicestatus'][recordIndex]['performance_data']):
      myPerfData = str(parsedServiceStatusContents['servicestatus'][recordIndex]['performance_data'])
   else:
      print("no performance data found for service name " + myServiceName + " and host name " + myHostName)

   

   ############################
   # 
   #  Parse Total Processes 
   # 
   ###################################


   if(myServiceName == "Total Processes"):
      extr = re.search('procs=(.+?)\;', myPerfData)
      totalProcs = extr.group(1)
      #print(myTimeStamp + "," + parsedServiceStatusContents['servicestatus'][recordIndex]['host_name'] + "," + parsedServiceStatusContents['servicestatus'][recordIndex]['performance_data'])
      totalProcessCsvFile.write(myTimeStamp + "," + parsedServiceStatusContents['servicestatus'][recordIndex]['host_name'] + "," + totalProcs + "\n")

   ############################
   # 
   #  Parse Swap Usage
   # 
   ###################################

   elif(myServiceName == "Swap Usage"):
      extr = re.search('swap=(.+?)MB\;', myPerfData)
      swap = extr.group(1)
      #print(myTimeStamp + "," + parsedServiceStatusContents['servicestatus'][recordIndex]['host_name'] + "," + parsedServiceStatusContents['servicestatus'][recordIndex]['performance_data'])
      swapUsageCsvFile.write(myTimeStamp + "," + parsedServiceStatusContents['servicestatus'][recordIndex]['host_name'] + "," + swap + "\n")

   ############################
   # 
   #  Parse Memory Data
   # 
   ###################################

   elif(myServiceName == "Memory Usage"):
      # Nagios appears to have a couple of different ways of displaying memory stats between different systems.
      # for Linux, it shows MB, for macOS, it shows in percentage used. I don't see a way of determining macOS 
      # usage in MB, so they will have to be zeroed out in the file for now. Perhaps a mediator that broke
      # out usage in MB and percentage used in two different files would be best.
      # I don't have a Windows or other operating systems to test at the moment.
      extr = re.search('total=(.+?)MB', myPerfData)
      if extr:
         memtotal = extr.group(1)
      else:
         memtotal = "0"
      extr = re.search('used=(.+?)MB', myPerfData)
      if extr:
         memused = extr.group(1)
      else:
         memused = "0"
      memoryDataCsvFile.write(myTimeStamp + "," + parsedServiceStatusContents['servicestatus'][recordIndex]['host_name'] + "," + memtotal + "," + memused + "\n")

      #################################
      #
      #  Memory usage .. not sure where we got commited/physical from in the original mediator
      #  It may be a custom plugin, which we need to document if it is the case. For now, just 
      #  zero these until we get more info.
      #
      #########################################################################################

      memoryUsageCsvFile.write(myTimeStamp + "," + parsedServiceStatusContents['servicestatus'][recordIndex]['host_name'] + ",0,0\n")
      #print(myTimeStamp + "," + parsedServiceStatusContents['servicestatus'][recordIndex]['host_name'] + "," + parsedServiceStatusContents['servicestatus'][recordIndex]['performance_data'])

   #################################
   #
   #  Parse diskUsage 
   #
   ##################################################

   # disk usage is a bit odd in Nagios. It appears that the filesystem is merged with the string "Disk Usage" in 
   # the name attribute for the record. Only found root filesystems, but assuming that other monitors can be created
   # for other filesystems, and the filesystem name would also be part of the 'name' attribute. So, assuming that is 
   # the case, we need to do a regex match on the name for ".*Disk Usage", and extract the filesystem from the name 
   # attribute. 
   # Disk usage *could* be customer-independent if there were monitoring needs beyond just root. For example, this 
   # nrpe plugin command allows a customer to monitor all mounted filesystems:
   #
   # command[check_disks]=/usr/lib/nagios/plugins/check_disk -w 20% -c 10% -C -W 20% -K 10% -p /*
   # 
   # The following parses only default Nagios monitoring shows root fs, and not any custom nrpe monitoring 
   elif(myServiceName == "/ Disk Usage"):
      extr = re.search('^(.+?) ', parsedServiceStatusContents['servicestatus'][recordIndex]['name'])
      diskName = extr.group(1)
      extr = re.search('=(.+?)MB', myPerfData)
      diskUsed = extr.group(1)
      extr = re.search('.*;(.*)', myPerfData)
      diskSize = extr.group(1)
      diskFree = int(diskSize) - int(diskUsed)
      #print("disk name: " + diskName + "disk used: " + str(diskUsed) + ", disk size: " + diskSize) 
      diskUsageCsvFile.write(myTimeStamp + "," + parsedServiceStatusContents['servicestatus'][recordIndex]['host_name'] + "," + diskName + "," + str(diskUsed) + "\n")


   #################################
   #
   #  Parse CPU Stats for cpuStats and cpuUsage files
   #
   ##################################################


   elif(myServiceName == "CPU Stats"):
      extr = re.search('user=(.+?)\%', myPerfData)
      cpuUser = extr.group(1)
      extr = re.search('system=(.+?)\%', myPerfData)
      cpuSystem = extr.group(1)
      extr = re.search('iowait=(.+?)\%', myPerfData)
      cpuIoWait = extr.group(1)
      extr = re.search('idle=(.+?)\%', myPerfData)
      cpuIdle = extr.group(1)
      cpuStatsCsvFile.write(myTimeStamp + "," + parsedServiceStatusContents['servicestatus'][recordIndex]['host_name'] + "," + cpuUser + "," + cpuSystem + "," + cpuIoWait + "," + cpuIdle + "\n")
      cpuUsage = float(cpuUser) + float(cpuSystem) + float(cpuIoWait)
      cpuUsageCsvFile.write(myTimeStamp + "," + parsedServiceStatusContents['servicestatus'][recordIndex]['host_name'] + "," + str(cpuUsage) + "\n")

   #################################
   #
   #  Parse users
   #
   ##################################################

   elif(myServiceName == "Users"):
      print(myPerfData)
      print(type(myPerfData))
      print(hostName)
      extr = re.search('users\=(.+?)\;', myPerfData)
      myUsers=extr.group(1)
      usersCsvFile.write(myTimeStamp + "," + parsedServiceStatusContents['servicestatus'][recordIndex]['host_name'] + "," + str(myUsers) + "\n")
      #print ("users")
      #print(myTimeStamp + "," + parsedServiceStatusContents['servicestatus'][recordIndex]['host_name'] + "," + parsedServiceStatusContents['servicestatus'][recordIndex]['performance_data'])

   #################################
   #
   #  Parse load5  
   #  Load average metrics can be under either "Load" or "Current Load", which is irritating
   #  Also - load5 returns 0.00 for macOS, which is also irritating
   #
   ###########################################################################################


   elif(myServiceName == "Current Load" or myServiceName == "Load"):
      extr = re.search('load5=(.+?)\;', myPerfData)
      load5=extr.group(1)
      currentLoadCsvFile.write(myTimeStamp + "," + parsedServiceStatusContents['servicestatus'][recordIndex]['host_name'] + "," + str(load5) + "\n")

   # end parse record, next record

   recordIndex = recordIndex + 1


hostStatusCsvFile.close
pingDataCsvFile.close
cpuStatsCsvFile.close
totalProcessCsvFile.close
swapUsageCsvFile.close
cpuUsageCsvFile.close
memoryDataCsvFile.close
usersCsvFile.close
memoryUsageCsvFile.close
diskUsageCsvFile.close
currentLoadCsvFile.close