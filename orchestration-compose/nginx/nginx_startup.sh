#!/bin/sh

confd -interval 30 &

/usr/sbin/nginx -g "daemon off;"
