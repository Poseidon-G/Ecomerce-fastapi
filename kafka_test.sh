#!/bin/bash

# Configuration
TOPIC="test-topic"
BROKER="localhost:9092"
NUM_MESSAGES=100000
MESSAGE_SIZE=1024  # 1KB
NUM_PRODUCERS=4
DURATION=60  # seconds

# Generate test data file
generate_messages() {
    local size=$1
    local num=$2
    local file=$3
    dd if=/dev/urandom bs=$size count=$num 2>/dev/null | base64 > $file
}

# Start producer
run_producer() {
    local producer_id=$1
    local messages_per_producer=$((NUM_MESSAGES / NUM_PRODUCERS))
    
    cat test_data.txt | while read line; do
        echo "{\"producer\": $producer_id, \"timestamp\": $(date +%s%N), \"data\": \"$line\"}"
    done | docker exec -i ecommerce_kafka kafka-console-producer \
        --broker-list $BROKER \
        --topic $TOPIC \
        --producer.config /tmp/producer.properties
}

# Start consumer with metrics
run_consumer() {
    docker exec ecommerce_kafka kafka-consumer-groups \
        --bootstrap-server $BROKER \
        --group stress-test-group \
        --describe \
        --members --verbose
}

# Monitor lag
monitor_lag() {
    while true; do
        docker exec ecommerce_kafka kafka-consumer-groups \
            --bootstrap-server $BROKER \
            --group stress-test-group \
            --describe > lag_metrics.txt
        sleep 5
    done
}

# Setup
echo "Generating test data..."
generate_messages $MESSAGE_SIZE $NUM_MESSAGES "test_data.txt"

# Create producer config
cat > producer.properties << EOF
batch.size=65536
linger.ms=5
compression.type=gzip
EOF
docker cp producer.properties ecommerce_kafka:/tmp/

# Start test
echo "Starting stress test..."
start_time=$(date +%s)

# Start producers in parallel
for i in $(seq 1 $NUM_PRODUCERS); do
    run_producer $i &
done

# Start monitoring
monitor_lag &
monitor_pid=$!

# Wait for duration
sleep $DURATION

# Cleanup
kill $monitor_pid
rm test_data.txt producer.properties

# Print results
end_time=$(date +%s)
total_time=$((end_time - start_time))
messages_per_sec=$((NUM_MESSAGES / total_time))

echo "=== Stress Test Results ==="
echo "Duration: $total_time seconds"
echo "Messages sent: $NUM_MESSAGES"
echo "Throughput: $messages_per_sec msg/sec"
echo "Consumer lag: $(tail -n 1 lag_metrics.txt)"