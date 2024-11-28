#!/bin/bash

TOPIC="test-topic"
BROKER="localhost:9092"

# Create topic if it doesn't exist
docker exec -it ecommerce_kafka kafka-topics --create --topic $TOPIC --bootstrap-server $BROKER --partitions 1 --replication-factor 1 || echo "Topic already exists."

# Publish a message
echo "Test Message" | docker exec -i ecommerce_kafka kafka-console-producer --broker-list $BROKER --topic $TOPIC

# Consume the message
docker exec -it ecommerce_kafka kafka-console-consumer --bootstrap-server $BROKER --topic $TOPIC --from-beginning --timeout-ms 5000 | grep "Test Message" && echo "Message Test Passed!" || echo "Message Test Failed!"
