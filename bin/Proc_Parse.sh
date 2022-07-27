#!/bin/bash

#### Variables and Files


NIFI_REPORTING_FILE="/var/SP/nifi/logs/nifi-reporting.log"
PROCESSOR_REPORTING_DATE=`grep ^20 ${NIFI_REPORTING_FILE} |tail -2 | grep "Processor Statuses" | awk '{print $1" "$2}'`
PROCESSOR_REPORTING_DATE_MOD=`grep ^20 ${NIFI_REPORTING_FILE} |tail -2 | grep "Processor Statuses" | awk '{print $1" "$2}' | awk -F"," '{print $1}'`
CONNECTION_REPORTING_DATE=`grep ^20 ${NIFI_REPORTING_FILE} |tail -2 | grep "Connection Statuses" | awk '{print $1" "$2}'`
CONNECTION_REPORTING_DATE_MOD=`grep ^20 ${NIFI_REPORTING_FILE} |tail -2 | grep "Connection Statuses" | awk '{print $1" "$2}'| awk -F"," '{print $1}'`
REPORTING_PROC_MOD_FILE="/var/SP/nifi/logs/Scripted_Out/nifi-proc.csv"
REPORTING_CONN_MOD_FILE="/var/SP/nifi/logs/Scripted_Out/nifi-conn.csv"

tac  ${NIFI_REPORTING_FILE} | sed -e '/'"$PROCESSOR_REPORTING_DATE"'/q' | tac > /tmp/Latest_Reporting.stat

{ sed -n '/'"${CONNECTION_REPORTING_DATE}"'/q;p'; cat >/tmp/Connection.stat; } < /tmp/Latest_Reporting.stat > /tmp/Processor.stat


grep -v "^-|Flow Files In|^20" /tmp/Processor.stat |sed -e 's/,/;/g' |awk -F"|" '{print $2","$3","$4","$5","$6","$7","$8","$9","$10","$11}' | sed -e's/  */ /g' | grep -v "^," |grep -v "Processor Name , Processor ID , Processor Type" |awk -v var="${PROCESSOR_REPORTING_DATE_MOD}" '{print var","$0}'

#grep -v "^-|Connection ID|^20" /tmp/Connection.stat |sed -e 's/,/;/g'|awk -F"|" '{print $2","$3","$4","$5","$6","$7","$8}' | sed -e's/  */ /g' | grep -v "^,"|grep -v "Connection ID , Source , Connection Name" |awk -v var="${CONNECTION_REPORTING_DATE_MOD}" '{print var","$0}' >> ${REPORTING_CONN_MOD_FILE}

