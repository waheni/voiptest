#!/bin/bash
# Debug script to simulate CI environment locally

set -e

echo "🔧 Simulating CI environment locally..."
echo ""

# Cleanup
echo "1. Cleaning up existing containers..."
docker stop asterisk-ci 2>/dev/null || true
docker rm asterisk-ci 2>/dev/null || true

# Start Asterisk like CI does
echo "2. Starting Asterisk container..."
docker run -d --name asterisk-ci \
  -p 5060:5060/udp \
  -p 5060:5060/tcp \
  -v $(pwd)/lab/asterisk/extensions.conf:/etc/asterisk/extensions.conf \
  -v $(pwd)/lab/asterisk/pjsip.conf:/etc/asterisk/pjsip.conf \
  andrius/asterisk:18

echo "   Waiting for Asterisk to start..."
sleep 15

# Build image like CI does
echo "3. Building Docker image..."
docker build -t voiptest-ci .

# Run test like CI does
echo "4. Running smoke test with --network host..."
docker run --rm --network host \
  -v $(pwd)/examples:/work/examples \
  voiptest-ci run examples/smoke_basic.yaml

# Cleanup
echo "5. Cleaning up..."
docker stop asterisk-ci
docker rm asterisk-ci

echo ""
echo "✅ CI simulation complete!"
