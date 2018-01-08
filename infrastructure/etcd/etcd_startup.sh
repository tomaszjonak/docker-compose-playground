#!/bin/sh
/usr/local/bin/etcd --config-file /etc/etcd/etcd.conf.yml &

sleep 1

/usr/local/bin/etcdctl mkdir lb
/usr/local/bin/etcdctl mkdir lb/upstream
/usr/local/bin/etcdctl mk lb/subdomain test_domain

wait

