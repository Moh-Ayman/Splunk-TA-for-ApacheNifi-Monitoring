# Splunk TA for ApacheNifi Monitoring
Splunk Technical Addon for Apache Nifi Monitoring is a customized Splunk App intended to Collect information from Nifi Reporting Tasks and Nifi APIs for Monitoring purposes and Store it into Splunk Index for Data Observability. 

Technical Addon is collecting:
    1- Processors Metrics from Processors Reporting Task

    2- Connections Metrics from Connections Reporting Task

    3- Apache Nifi Cluster Diagnostics Metrics
    
    4- Mapping info between Processor Groups and it's corresponding processors underneath

    5- Mapping (Lineage) between Processors and Connections

TA is collecting data from APIs & Logs, Transform it to corresponding needed info and then store it in Splunk Index.