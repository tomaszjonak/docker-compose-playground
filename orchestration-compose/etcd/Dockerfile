from quay.io/coreos/etcd:v3.3

copy etcd.conf.yml /etc/etcd/etcd.conf.yml
copy etcd_startup.sh etcd_startup.sh

cmd ["/bin/sh", "-c", "./etcd_startup.sh"]

