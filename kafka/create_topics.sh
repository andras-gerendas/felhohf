#!/bin/bash

# Based on: https://github.com/wurstmeister/kafka-docker/blob/master/create-topics.sh

KAFKA_PORT=9092

if [[ -z "$START_TIMEOUT" ]]; then
    START_TIMEOUT=600
fi

start_timeout_exceeded=false
count=0
step=10
while netstat -lnt | awk '$4 ~ /:'"$KAFKA_PORT"'$/ {exit 1}'; do
    echo "waiting for kafka to be ready"
    sleep $step;
    count=$((count + step))
    if [ $count -gt $START_TIMEOUT ]; then
        start_timeout_exceeded=true
        break
    fi
done

if $start_timeout_exceeded; then
    echo "Not able to auto-create topic (waited for $START_TIMEOUT sec)"
    exit 1
fi

sh /opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --create --topic ocr-completed --partitions 1 --replication-factor 1 --if-not-exists
sh /opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --create --topic image-uploaded --partitions 6 --replication-factor 1 --if-not-exists
sh /opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --topic image-uploaded --alter --partitions 6

wait