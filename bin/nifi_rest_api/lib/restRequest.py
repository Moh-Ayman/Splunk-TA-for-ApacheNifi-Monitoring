import json
import csv
import getpass
import datetime
import argparse
import sys
from time import sleep

import csv
import gzip
import datetime

import sys
import json
import os
import base64
import string
import random
import requests
import socket
import smtplib
import re
requests.packages.urllib3.disable_warnings()
counter=0
def format_time():
    try:
        t = datetime.datetime.now()
        s = t.strftime('%m-%d-%Y %H:%M:%S.%f')
        return s[:-3]
    except (ValueError,IOError) as err:
        #log(" - Main() -- Error Occured \n"+str(err),"e")
        print(" - Main() -- Error Occured \n"+str(err),"e")

def log(message,status):
    try:
        if status=="e":
                f.write(format_time() + " -0000 ERROR " + str(message)+"\n")
                print(format_time() + " -0000 ERROR " + str(message)+"\n")
        elif status=="s":
                f.write(format_time() + " -0000 SUCCESS " + str(message)+"\n")
                print(format_time() + " -0000 SUCCESS " + str(message)+"\n")
        elif status=="n":
                f.write(format_time() + " -0000 INFO " + str(message)+"\n")
                print(format_time() + " -0000 INFO " + str(message)+"\n")
        elif status=="w":
                f.write(format_time() + " -0000 WARNING " + str(message)+"\n")
                print(format_time() + " -0000 WARNING " + str(message)+"\n")
        elif status=="d":
                f.write(format_time() + " -0000 Data " + str(message)+"\n")
                print(format_time() + " -0000 Data " + str(message)+"\n")
    except (ValueError,IOError) as err:
        #log(" - log() -- Error Occured \n"+str(err),"e")
        print(" - log() -- Error Occured \n"+str(err),"e")

def RestReq(METHOD,ENDPOINT):
    try:
        ConfPath = '../conf/'

        clientCrt = ConfPath+"<CERT FILENAME>"
        clientKey = ConfPath+"<KEY FILENAME>"
        url = "https://<HOSTNAME:PORT>/nifi-api"+ENDPOINT

        headers = {'content-type': 'application/json'}
        os.environ['NO_PROXY'] = '<HOSTNAME>'
        r = requests.get(url,verify=False,  headers=headers, cert=(clientCrt, clientKey))
        text =r.text
        if re.match("\{.*\}", text):
            text_json=json.dumps(json.loads(text), indent=4, sort_keys=True)

        else:
            text_json=text

        global counter
        counter=counter+1
        return text_json
    except (ValueError,IOError) as err:
        print(" - RestReq() -- Error Occured \n"+str(err))
        sys.exit(1)


def _curl(METHOD,ENDPOINT):
    try:
        cmd="curl"
        opt="-ks --cert "+path+"/../conf/certs/<CERT FILENAME>.pem  --key "+path+"/../conf/certs/<PEM FILENAME>.pem -X "+str(METHOD)+" -H 'Accept-Encoding: gzip, deflate, br' -H 'Content-Type: application/x-www-form-urlencoded; charset=UTF-8' -H 'Accept: */*' --compressed"
        arg="https://<HOSTNAME:PORT>/nifi-api"+str(ENDPOINT)
        COMMAND=str(cmd)+" "+str(opt)+" "+arg
        out = subprocess.Popen(COMMAND, shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        stdout,stderr = out.communicate()
        text = stdout
        if re.match("\{.*\}", text):
            text_json=json.dumps(json.loads(text), indent=4, sort_keys=True)
        else:
            text_json=text
        return text_json
    except (ValueError,IOError) as err:
      print(" - Main() -- Error Occured \n"+str(err))

def TreeTrace(parent,text_json):
    ProcessorGroups=[]
    PGDICT={}
    PDICT={}
    Prcessors=[]
    json_data = json.loads(text_json)    
    NumProcessGroups=len(json_data['processGroupFlow']['flow']['processGroups'])
    for i in range(NumProcessGroups):
        PGDICT={}
        PGName=json_data['processGroupFlow']['flow']['processGroups'][i]['component']['name']
        PGId=json_data['processGroupFlow']['flow']['processGroups'][i]['component']['id']
        PGcomments=json_data['processGroupFlow']['flow']['processGroups'][i]['component']['comments']       

        PGDICT.update({"Name":str(PGName)})
        PGDICT.update({"Id":str(PGId)})
        PGDICT.update({"comments":str(PGcomments)})

        PGDICT.update({"ParentName":str(parent["Name"])})
        PGDICT.update({"ParentId":str(parent["Id"])})
        ProcessorGroups.append(PGDICT)

        
    NumProcessGroups=len(json_data['processGroupFlow']['flow']['processors'])
    for i in range(NumProcessGroups): 
        PDICT={}
        PName=json_data['processGroupFlow']['flow']['processors'][i]['component']['name']
        PId=json_data['processGroupFlow']['flow']['processors'][i]['component']['id']
        Pcomments=json_data['processGroupFlow']['flow']['processors'][i]['component']['config']['comments'] 
        
        PDICT.update({"Name":str(PName)})
        PDICT.update({"Id":str(PId)})
        PDICT.update({"comments":str(Pcomments)})                        

        PDICT.update({"ParentName":str(parent["Name"])})
        PDICT.update({"ParentId":str(parent["Id"])})

        Prcessors.append(PDICT)
    return ProcessorGroups,Prcessors

def Proc_ProcGrp_Lookup(METHOD,ENDPOINT):
    try:
        ParentPGs=[ {"Name":"root","Id":"root"} ]
        for PPGs in ParentPGs:
            text_json=RestReq("GET","/flow/process-groups/"+str(PPGs["Id"]))
            ProcessorGroups,Prcessors=TreeTrace(PPGs,text_json)
            for ProcGRP in ProcessorGroups:
                ParentPGs.append({"Name":str(ProcGRP["Name"]),"Id":str(ProcGRP["Id"])})
                print(str(format_time())+","+str(ProcGRP["ParentName"])+","+str(ProcGRP["ParentId"])+","+str(ProcGRP["Name"])+","+str(ProcGRP["Id"])+",Processor_Group"+","+str(ProcGRP["comments"]))
            for Procs in Prcessors:
                print(str(format_time())+","+str(Procs["ParentName"])+","+str(Procs["ParentId"])+","+str(Procs["Name"])+","+str(Procs["Id"])+",Processor"+","+str(Procs["comments"]))
    except (ValueError,IOError) as err:
       print(" - Main() -- Error Occured \n"+str(err))


def nifi_utalization_metrics(METHOD,ENDPOINT):
    try:
        Metrics=[]
        mtricsDICT={}
        text_json=RestReq("GET",str(ENDPOINT))
        json_data = json.loads(text_json)
        availableProcessors=json_data['systemDiagnostics']['aggregateSnapshot']['availableProcessors']
        contentRepositoryStorageUsage_freeSpace=json_data['systemDiagnostics']['aggregateSnapshot']['contentRepositoryStorageUsage'][0]['freeSpace']
        contentRepositoryStorageUsage_freeSpaceBytes=json_data['systemDiagnostics']['aggregateSnapshot']['contentRepositoryStorageUsage'][0]['freeSpaceBytes']
        contentRepositoryStorageUsage_identifier=json_data['systemDiagnostics']['aggregateSnapshot']['contentRepositoryStorageUsage'][0]['identifier']
        contentRepositoryStorageUsage_totalSpace=json_data['systemDiagnostics']['aggregateSnapshot']['contentRepositoryStorageUsage'][0]['totalSpace']
        contentRepositoryStorageUsage_totalSpaceBytes=json_data['systemDiagnostics']['aggregateSnapshot']['contentRepositoryStorageUsage'][0]['totalSpaceBytes']
        contentRepositoryStorageUsage_usedSpace=json_data['systemDiagnostics']['aggregateSnapshot']['contentRepositoryStorageUsage'][0]['usedSpace']
        contentRepositoryStorageUsage_usedSpaceBytes=json_data['systemDiagnostics']['aggregateSnapshot']['contentRepositoryStorageUsage'][0]['usedSpaceBytes']
        contentRepositoryStorageUsage_utilization=json_data['systemDiagnostics']['aggregateSnapshot']['contentRepositoryStorageUsage'][0]['utilization']
        daemonThreads=json_data['systemDiagnostics']['aggregateSnapshot']['daemonThreads']
        flowFileRepositoryStorageUsage_freeSpace=json_data['systemDiagnostics']['aggregateSnapshot']['flowFileRepositoryStorageUsage']['freeSpace']
        flowFileRepositoryStorageUsage_freeSpaceBytes=json_data['systemDiagnostics']['aggregateSnapshot']['flowFileRepositoryStorageUsage']['freeSpaceBytes']
        flowFileRepositoryStorageUsage_totalSpace=json_data['systemDiagnostics']['aggregateSnapshot']['flowFileRepositoryStorageUsage']['totalSpace']
        flowFileRepositoryStorageUsage_totalSpaceBytes=json_data['systemDiagnostics']['aggregateSnapshot']['flowFileRepositoryStorageUsage']['totalSpaceBytes']
        flowFileRepositoryStorageUsage_usedSpace=json_data['systemDiagnostics']['aggregateSnapshot']['flowFileRepositoryStorageUsage']['usedSpace']
        flowFileRepositoryStorageUsage_usedSpaceBytes=json_data['systemDiagnostics']['aggregateSnapshot']['flowFileRepositoryStorageUsage']['usedSpaceBytes']
        flowFileRepositoryStorageUsage_utilization=json_data['systemDiagnostics']['aggregateSnapshot']['flowFileRepositoryStorageUsage']['utilization']
        freeHeap=json_data['systemDiagnostics']['aggregateSnapshot']['freeHeap']
        freeHeapBytes=json_data['systemDiagnostics']['aggregateSnapshot']['freeHeapBytes']
        freeNonHeap=json_data['systemDiagnostics']['aggregateSnapshot']['freeNonHeap']
        freeNonHeapBytes=json_data['systemDiagnostics']['aggregateSnapshot']['freeNonHeapBytes']
        heapUtilization=json_data['systemDiagnostics']['aggregateSnapshot']['heapUtilization']
        maxHeap=json_data['systemDiagnostics']['aggregateSnapshot']['maxHeap']
        maxHeapBytes=json_data['systemDiagnostics']['aggregateSnapshot']['maxHeapBytes']
        maxNonHeap=json_data['systemDiagnostics']['aggregateSnapshot']['maxNonHeap']
        maxNonHeapBytes=json_data['systemDiagnostics']['aggregateSnapshot']['maxNonHeapBytes']
        processorLoadAverage=json_data['systemDiagnostics']['aggregateSnapshot']['processorLoadAverage']
        provenanceRepositoryStorageUsage_freeSpace=json_data['systemDiagnostics']['aggregateSnapshot']['provenanceRepositoryStorageUsage'][0]['freeSpace']
        provenanceRepositoryStorageUsage_freeSpaceBytes=json_data['systemDiagnostics']['aggregateSnapshot']['provenanceRepositoryStorageUsage'][0]['freeSpaceBytes']
        provenanceRepositoryStorageUsage_identifier=json_data['systemDiagnostics']['aggregateSnapshot']['provenanceRepositoryStorageUsage'][0]['identifier']
        provenanceRepositoryStorageUsage_totalSpace=json_data['systemDiagnostics']['aggregateSnapshot']['provenanceRepositoryStorageUsage'][0]['totalSpace']
        provenanceRepositoryStorageUsage_totalSpaceBytes=json_data['systemDiagnostics']['aggregateSnapshot']['provenanceRepositoryStorageUsage'][0]['totalSpaceBytes']
        provenanceRepositoryStorageUsage_usedSpace=json_data['systemDiagnostics']['aggregateSnapshot']['provenanceRepositoryStorageUsage'][0]['usedSpace']
        provenanceRepositoryStorageUsage_usedSpaceBytes=json_data['systemDiagnostics']['aggregateSnapshot']['provenanceRepositoryStorageUsage'][0]['usedSpaceBytes']
        provenanceRepositoryStorageUsage_utilization=json_data['systemDiagnostics']['aggregateSnapshot']['provenanceRepositoryStorageUsage'][0]['utilization']
        statsLastRefreshed=json_data['systemDiagnostics']['aggregateSnapshot']['statsLastRefreshed']
        totalHeap=json_data['systemDiagnostics']['aggregateSnapshot']['totalHeap']
        totalHeapBytes=json_data['systemDiagnostics']['aggregateSnapshot']['totalHeapBytes']
        totalNonHeap=json_data['systemDiagnostics']['aggregateSnapshot']['totalNonHeap']
        totalNonHeapBytes=json_data['systemDiagnostics']['aggregateSnapshot']['totalNonHeapBytes']
        totalThreads=json_data['systemDiagnostics']['aggregateSnapshot']['totalThreads']
        uptime=json_data['systemDiagnostics']['aggregateSnapshot']['uptime']
        usedHeap=json_data['systemDiagnostics']['aggregateSnapshot']['usedHeap']
        usedHeapBytes=json_data['systemDiagnostics']['aggregateSnapshot']['usedHeapBytes']
        usedNonHeap=json_data['systemDiagnostics']['aggregateSnapshot']['usedNonHeap']
        usedNonHeapBytes=json_data['systemDiagnostics']['aggregateSnapshot']['usedNonHeapBytes']
        versionInfo_buildTag=json_data['systemDiagnostics']['aggregateSnapshot']['versionInfo']['buildTag']
        versionInfo_buildTimestamp=json_data['systemDiagnostics']['aggregateSnapshot']['versionInfo']['buildTimestamp']
        versionInfo_javaVendor=json_data['systemDiagnostics']['aggregateSnapshot']['versionInfo']['javaVendor']
        versionInfo_javaVersion=json_data['systemDiagnostics']['aggregateSnapshot']['versionInfo']['javaVersion']
        versionInfo_niFiVersion=json_data['systemDiagnostics']['aggregateSnapshot']['versionInfo']['niFiVersion']
        versionInfo_osArchitecture=json_data['systemDiagnostics']['aggregateSnapshot']['versionInfo']['osArchitecture']
        versionInfo_osName=json_data['systemDiagnostics']['aggregateSnapshot']['versionInfo']['osName']
        versionInfo_osVersion=json_data['systemDiagnostics']['aggregateSnapshot']['versionInfo']['osVersion']
        mtricsDICT.update({"availableProcessors":str(availableProcessors)})
        mtricsDICT.update({"contentRepositoryStorageUsage_freeSpace":str(contentRepositoryStorageUsage_freeSpace)})
        mtricsDICT.update({"contentRepositoryStorageUsage_freeSpaceBytes":str(contentRepositoryStorageUsage_freeSpaceBytes)})
        mtricsDICT.update({"contentRepositoryStorageUsage_identifier":str(contentRepositoryStorageUsage_identifier)})
        mtricsDICT.update({"contentRepositoryStorageUsage_totalSpace":str(contentRepositoryStorageUsage_totalSpace)})
        mtricsDICT.update({"contentRepositoryStorageUsage_totalSpaceBytes":str(contentRepositoryStorageUsage_totalSpaceBytes)})
        mtricsDICT.update({"contentRepositoryStorageUsage_usedSpace":str(contentRepositoryStorageUsage_usedSpace)})
        mtricsDICT.update({"contentRepositoryStorageUsage_usedSpaceBytes":str(contentRepositoryStorageUsage_usedSpaceBytes)})
        mtricsDICT.update({"contentRepositoryStorageUsage_utilization":str(contentRepositoryStorageUsage_utilization)})
        mtricsDICT.update({"daemonThreads":str(daemonThreads)})
        mtricsDICT.update({"flowFileRepositoryStorageUsage_freeSpace":str(flowFileRepositoryStorageUsage_freeSpace)})
        mtricsDICT.update({"flowFileRepositoryStorageUsage_freeSpaceBytes":str(flowFileRepositoryStorageUsage_freeSpaceBytes)})
        mtricsDICT.update({"flowFileRepositoryStorageUsage_totalSpace":str(flowFileRepositoryStorageUsage_totalSpace)})
        mtricsDICT.update({"flowFileRepositoryStorageUsage_totalSpaceBytes":str(flowFileRepositoryStorageUsage_totalSpaceBytes)})
        mtricsDICT.update({"flowFileRepositoryStorageUsage_usedSpace":str(flowFileRepositoryStorageUsage_usedSpace)})
        mtricsDICT.update({"flowFileRepositoryStorageUsage_usedSpaceBytes":str(flowFileRepositoryStorageUsage_usedSpaceBytes)})
        mtricsDICT.update({"flowFileRepositoryStorageUsage_utilization":str(flowFileRepositoryStorageUsage_utilization)})
        mtricsDICT.update({"freeHeap":str(freeHeap)})
        mtricsDICT.update({"freeHeapBytes":str(freeHeapBytes)})
        mtricsDICT.update({"freeNonHeap":str(freeNonHeap)})
        mtricsDICT.update({"freeNonHeapBytes":str(freeNonHeapBytes)})
        mtricsDICT.update({"heapUtilization":str(heapUtilization)})
        mtricsDICT.update({"maxHeap":str(maxHeap)})
        mtricsDICT.update({"maxHeapBytes":str(maxHeapBytes)})
        mtricsDICT.update({"maxNonHeap":str(maxNonHeap)})
        mtricsDICT.update({"maxNonHeapBytes":str(maxNonHeapBytes)})
        mtricsDICT.update({"processorLoadAverage":str(processorLoadAverage)})
        mtricsDICT.update({"provenanceRepositoryStorageUsage_freeSpace":str(provenanceRepositoryStorageUsage_freeSpace)})
        mtricsDICT.update({"provenanceRepositoryStorageUsage_freeSpaceBytes":str(provenanceRepositoryStorageUsage_freeSpaceBytes)})
        mtricsDICT.update({"provenanceRepositoryStorageUsage_identifier":str(provenanceRepositoryStorageUsage_identifier)})
        mtricsDICT.update({"provenanceRepositoryStorageUsage_totalSpace":str(provenanceRepositoryStorageUsage_totalSpace)})
        mtricsDICT.update({"provenanceRepositoryStorageUsage_totalSpaceBytes":str(provenanceRepositoryStorageUsage_totalSpaceBytes)})
        mtricsDICT.update({"provenanceRepositoryStorageUsage_usedSpace":str(provenanceRepositoryStorageUsage_usedSpace)})
        mtricsDICT.update({"provenanceRepositoryStorageUsage_usedSpaceBytes":str(provenanceRepositoryStorageUsage_usedSpaceBytes)})
        mtricsDICT.update({"provenanceRepositoryStorageUsage_utilization":str(provenanceRepositoryStorageUsage_utilization)})
        mtricsDICT.update({"statsLastRefreshed":str(statsLastRefreshed)})
        mtricsDICT.update({"totalHeap":str(totalHeap)})
        mtricsDICT.update({"totalHeapBytes":str(totalHeapBytes)})
        mtricsDICT.update({"totalNonHeap":str(totalNonHeap)})
        mtricsDICT.update({"totalNonHeapBytes":str(totalNonHeapBytes)})
        mtricsDICT.update({"totalThreads":str(totalThreads)})
        mtricsDICT.update({"uptime":str(uptime)})
        mtricsDICT.update({"usedHeap":str(usedHeap)})
        mtricsDICT.update({"usedHeapBytes":str(usedHeapBytes)})
        mtricsDICT.update({"usedNonHeap":str(usedNonHeap)})
        mtricsDICT.update({"usedNonHeapBytes":str(usedNonHeapBytes)})
        mtricsDICT.update({"versionInfo_buildTag":str(versionInfo_buildTag)})
        mtricsDICT.update({"versionInfo_buildTimestamp":str(versionInfo_buildTimestamp)})
        mtricsDICT.update({"versionInfo_javaVendor":str(versionInfo_javaVendor)})
        mtricsDICT.update({"versionInfo_javaVersion":str(versionInfo_javaVersion)})
        mtricsDICT.update({"versionInfo_niFiVersion":str(versionInfo_niFiVersion)})
        mtricsDICT.update({"versionInfo_osArchitecture":str(versionInfo_osArchitecture)})
        mtricsDICT.update({"versionInfo_osName":str(versionInfo_osName)})
        DICT_json={}
        DICT_json = json.dumps(mtricsDICT, sort_keys=True)
        nifi_metrics_file.write(DICT_json)
        print(str(DICT_json))
    except (ValueError,IOError) as err:
       f.write(" - Main() -- Error Occured \n"+str(err))




def Main(API,path):
     f = open(path+"/Artifacts.json", "w")
     if API == "/flow/process-groups/":
           global file
           file = open(path+"/lookup.csv", "w")
           Proc_ProcGrp_Lookup("GET",API)
     elif API == "/system-diagnostics":
           global nifi_metrics_file
           nifi_metrics_file = open(path+"/nifi_utalization_metrics.json", "w")
           nifi_utalization_metrics("GET",API)
     else:
           text_json=RestReq("GET",API)

args=sys.argv
path=args[1]
API=args[2]



f = open(path+"/Artifacts.json", "w")

global protocol
global certs_path
global host
global port

CONF_File=str(path)+"/../conf/properties.conf"
with open(CONF_File, "r") as a_file:
  for line in a_file:
    if "splunk_nifi_monitoring_TA_protocol" in line:
      protocol = line.split("=")[1].rstrip("\n")
    if "splunk_nifi_monitoring_TA_certs_path" in line:
      certs_path = line.split("=")[1].rstrip("\n")
    if "splunk_nifi_monitoring_TA_host" in line:
      host = line.split("=")[1].rstrip("\n")
    if "splunk_nifi_monitoring_TA_port" in line:
      port = line.split("=")[1].rstrip("\n")

Main(API,path)
