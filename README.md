# Cloud Regions Latency  
Tool to measure inter-region latencies for public cloud provider - Azure

### Goals:  
- create a tool to automatically measures inter-region latencies for Azure
- measure the latencies between region
- create a heatmap from results
- measure impact of using CDN on download time from all regions compared to downloading from bucket   

### Tools:  
- Python3
- Bash
  
### Services:  
- Azure VM   
- Azure Storage 
- Azure FrontDoor and CDN

### Work plan:  
- create a script that takes care of provisioning VM instances ✓
- create a script that connects to vm by ssh and pings all other instances ✓
- run measurements for all available regions ✓
- create heatmap from results ✓
- extend support for CDNs and run measurements ✓
- create barplot from results ✓

### References:  
[Similar project](https://medium.com/@sachinkagarwal/public-cloud-inter-region-network-latency-as-heat-maps-134e22a5ff19)  
