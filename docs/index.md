# Cloud_regions_latency  
Tool to measure inter-region latencies for public cloud providers (AWS, GCP, Azure)  

### Goals:  
- create a tool to automatically measures inter-region latencies of public cloud providers  
- measure the latencies  
- create a heatmap   
- BONUS: measure impact of using CDN on latency compared to bare bucket-file hosting  

### Tools:  
- Python   
- Ansible?  
- Bash  
  
### Services:  
- EC2/GCE/Azure VM  
- DynamoDB and alternatives  
- S3 and alternatives  

### Work plan:  
- create a script that takes care of provisioning VM instances  
- set up config for VMs that pings each available instances and writes result to one location  
- run experments    
- create heatmap from results  
- extend support for CDNs and run experiments  

### References:  
[Similar project](https://medium.com/@sachinkagarwal/public-cloud-inter-region-network-latency-as-heat-maps-134e22a5ff19)  
