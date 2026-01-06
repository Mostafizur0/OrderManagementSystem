#!/bin/bash

set -e

echo "Building Docker images for Kubernetes deployment..."

# Build users service image
echo "Building users service image..."
cd ../fastapi-users-service
docker build -t users-service:latest .
cd -

# Build orders service image
echo "Building orders service image..."
cd ../orders-service
docker build -t orders-service:latest .
cd -

echo "Docker images built successfully!"
echo ""
echo "Images created:"
echo "- users-service:latest"
echo "- orders-service:latest"
echo ""
echo "If using a local cluster (like minikube, kind, or docker-desktop),"
echo "you may need to load the images into the cluster:"
echo ""
echo "# For minikube:"
echo "minikube image load users-service:latest"
echo "minikube image load orders-service:latest"
echo ""
echo "# For kind:"
echo "kind load docker-image users-service:latest"
echo "kind load docker-image orders-service:latest"
echo ""
echo "# For docker-desktop:"
echo "Images should be available automatically"
