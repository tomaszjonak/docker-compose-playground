# docker-compose-playground
Simple container structure to test docker features. There's going to be load balancer, some data receivers putting stuff to redis instance and worker pool eating redis data.

# Goals
- Make docker-compose file for each "independent" part
- orchestrate data receivers to announce themselves on load balancer
- throw prometheus in the mix to visualise whats working
- make receivers and workers "automatically" scallable
- use etcdb to make 

# Notes
- not using swarm/kubernets yet, I'd like to keep this somewhat simple
- catalogue structure wont be state of art for sure, I'm yet to discover some sane convention
