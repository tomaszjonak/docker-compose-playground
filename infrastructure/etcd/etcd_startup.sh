#!/bin/sh
/usr/local/bin/etcd --config-file /etc/etcd/etcd.conf.yml &

sleep 1

/usr/local/bin/etcdctl mkdir lb 2>&1 1>/dev/null
/usr/local/bin/etcdctl mkdir lb/upstream 2>&1 1>/dev/null
/usr/local/bin/etcdctl mk lb/subdomain test_domain 2>&1 1>/dev/null

wait

