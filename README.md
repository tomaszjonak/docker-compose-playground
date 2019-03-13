# docker-compose-playground
Simple container structure to test docker features. There's going to be load balancer, some data receivers putting stuff to redis instance and worker pool eating redis data.

# Goals
- [ ] ~~Make docker-compose file for each "independent" part~~ (turns out it's not convenient in any way)
- [X] use etcdb to store configuration data (this thing gave me headache)
- [X] orchestrate data receivers to announce themselves on load balancer
- [X] make receivers and workers "automatically" scallable
- [X] throw prometheus/grafana in the mix to visualise whats working
- [ ] Add autoconfiguration of grafana dashboards
- [ ] \(when graphana 5 is out) configure prometheus data source in graphana out of the box
- [ ] Use docker provided dns for service discovery

# Notes
- not using swarm/kubernets yet, I'd like to keep this somewhat simple
- catalogue structure wont be state of art for sure, I'm yet to discover some sane convention

# How to run this thing
1. go into infrastructure folder
2. install docker-compose through pip
3. run announce.py using python3 (2 should work but was never tested) (this call blocks)
4. Build all containers
```
docker-compose build
```
5. Startup whole thing (this call blocks and shows logs from each instance)
```
docker-compose up
```
6. Log in to grafana localhost:3000 (admin:admin)
7. Connect prometheus data source (when grafana 5.0 gets released this wont be necessary any longer)

| field  | value                                   |
| ------ | --------------------------------------- |
| URL    | http://infrastructure_prometheus_1:9090 |
| Access | Proxy                                   |

Leave rest as defaults
8. Import service dashboard (/infrastructure/grafana/monitoring.json) and set data source to prometheus
7. trigger some work from localhost (mess with secret or invalid payload structure)
```
curl localhost:80 -XPOST -d '{"secret": "c4bbcb1fbec99d65bf59d85c8cb62ee2db963f0fe106f483d9afa73bd4e39a8a", "data": "some_data"}'
```

# How to scale things up
Fetchers/processors can be scaled: to do so use
docker-compose up -d --scale fetcher=\<amount\> --scale processor=\<amount\>

It's convinient to have few consoles visible, one for result of docker-compose up another for announce.py and working one to modify state.
