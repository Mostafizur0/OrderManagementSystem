#!/bin/bash

# Setup script for MetalLB LoadBalancer in Kind cluster
# This enables LoadBalancer services to get external IPs

set -e

echo "Setting up MetalLB for LoadBalancer support in Kind cluster..."

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo "Error: kubectl is not installed or not in PATH"
    exit 1
fi

# Check if cluster is accessible
if ! kubectl cluster-info &> /dev/null; then
    echo "Error: Cannot connect to Kubernetes cluster"
    exit 1
fi

echo "Installing MetalLB..."
kubectl apply -f https://raw.githubusercontent.com/metallb/metallb/v0.13.12/config/manifests/metallb-native.yaml

echo "Waiting for MetalLB to be ready..."
kubectl wait --namespace metallb-system \
  --for=condition=ready pod \
  --selector=app=metallb \
  --timeout=90s

echo ""
echo "MetalLB installed successfully!"
echo ""
echo "Now you need to configure an IP address pool."
echo ""
echo "For Kind clusters, you can use the Docker network range."
echo "Common ranges:"
echo "  - 172.18.255.200-172.18.255.250 (Docker default)"
echo "  - 172.17.0.200-172.17.0.250 (Alternative)"
echo ""

# Detect Kind cluster network
KIND_NETWORK=$(docker network ls | grep kind | awk '{print $1}' | head -1)
if [ -n "$KIND_NETWORK" ]; then
    NETWORK_INFO=$(docker network inspect $KIND_NETWORK 2>/dev/null | grep -A 5 "IPAM" | grep "Subnet" | head -1 | cut -d'"' -f4)
    if [ -n "$NETWORK_INFO" ]; then
        echo "Detected Kind network: $NETWORK_INFO"
        echo "You can use a range within this network."
    fi
fi

read -p "Enter IP address pool (e.g., 172.18.255.200-172.18.255.250) or press Enter to skip: " IP_POOL

if [ -z "$IP_POOL" ]; then
    echo ""
    echo "Skipping IP pool configuration."
    echo "You can configure it manually later using:"
    echo ""
    echo "cat <<EOF | kubectl apply -f -"
    echo "apiVersion: metallb.io/v1beta1"
    echo "kind: IPAddressPool"
    echo "metadata:"
    echo "  name: default-pool"
    echo "  namespace: metallb-system"
    echo "spec:"
    echo "  addresses:"
    echo "  - YOUR_IP_RANGE_HERE"
    echo "EOF"
    echo ""
    echo "cat <<EOF | kubectl apply -f -"
    echo "apiVersion: metallb.io/v1beta1"
    echo "kind: L2Advertisement"
    echo "metadata:"
    echo "  name: default"
    echo "  namespace: metallb-system"
    echo "spec:"
    echo "  ipAddressPools:"
    echo "  - default-pool"
    echo "EOF"
    exit 0
fi

echo ""
echo "Configuring IP address pool: $IP_POOL"

cat <<EOF | kubectl apply -f -
apiVersion: metallb.io/v1beta1
kind: IPAddressPool
metadata:
  name: default-pool
  namespace: metallb-system
spec:
  addresses:
  - $IP_POOL
EOF

cat <<EOF | kubectl apply -f -
apiVersion: metallb.io/v1beta1
kind: L2Advertisement
metadata:
  name: default
  namespace: metallb-system
spec:
  ipAddressPools:
  - default-pool
EOF

echo ""
echo "MetalLB configured successfully!"
echo ""
echo "You can now deploy services with LoadBalancer type."
echo "Check status: kubectl get svc -A"
echo ""
echo "After deploying Kong, check its external IP:"
echo "kubectl get svc kong-proxy -n microservices-stack"

