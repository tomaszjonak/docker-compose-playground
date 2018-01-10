# docker-compose-playground
Simple container structure to test docker features. There's going to be load balancer, some data receivers putting stuff to redis instance and worker pool eating redis data.

# Goals
- [ ] ~~Make docker-compose file for each "independent" part~~ (turns out it's not convinient in any way)
- [X] use etcdb to store configuration data (this thing gave me headache)
- [X] orchestrate data receivers to announce themselves on load balancer
- [X] make receivers and workers "automatically" scallable
- [ ] throw prometheus/grafana in the mix to visualise whats working

# Notes
- not using swarm/kubernets yet, I'd like to keep this somewhat simple
- catalogue structure wont be state of art for sure, I'm yet to discover some sane convention

# How to run this thing
1. go into infrastructure folder
2. install docker-compose through pip
3. run announce.py using python3 (2 should work but was never tested) (this call blocks)
4. docker-compose build
5. docker-compose up (this call blocks)

Fetchers/processors can be scaled: to do so use
docker-compose up -d --scale fetcher=<amount> --scale processor=<amount>

It's convinient to have few consoles visible, one for result of docker-compose up another for announce.py and working one to modify state.
