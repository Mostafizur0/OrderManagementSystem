#!/bin/bash

set -e

echo "Deploying microservices stack to Kubernetes..."

# Apply namespace and network policies
echo "Creating namespace and network policies..."
kubectl apply -f namespace.yaml

# Apply infrastructure components first
echo "Deploying infrastructure components..."
kubectl apply -f postgres.yaml
kubectl apply -f infrastructure.yaml

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
kubectl wait --for=condition=ready pod -l app=postgres -n microservices-stack --timeout=120s

# Apply monitoring components
echo "Deploying monitoring components..."
kubectl apply -f monitoring-configmaps.yaml
kubectl apply -f prometheus.yaml
kubectl apply -f alertmanager.yaml
kubectl apply -f grafana.yaml

# Apply application services
echo "Deploying application services..."
kubectl apply -f users-service.yaml
kubectl apply -f orders-service.yaml

# Wait for services to be ready
echo "Waiting for services to be ready..."
echo "Note: Services may take 60-90 seconds to start (database migrations, etc.)"

# Wait for users-service with better error handling
if ! kubectl wait --for=condition=ready pod -l app=users-service -n microservices-stack --timeout=180s 2>/dev/null; then
  echo "Warning: users-service pods not ready after 180s. Checking status..."
  kubectl get pods -l app=users-service -n microservices-stack
  echo ""
  echo "Recent logs from users-service pods:"
  kubectl logs -l app=users-service -n microservices-stack --tail=20 || true
  echo ""
  echo "Continuing deployment anyway..."
fi

# Wait for orders-service with better error handling
if ! kubectl wait --for=condition=ready pod -l app=orders-service -n microservices-stack --timeout=180s 2>/dev/null; then
  echo "Warning: orders-service pods not ready after 180s. Checking status..."
  kubectl get pods -l app=orders-service -n microservices-stack
  echo ""
  echo "Recent logs from orders-service pods:"
  kubectl logs -l app=orders-service -n microservices-stack --tail=20 || true
  echo ""
  echo "Continuing deployment anyway..."
fi

# Apply Kong proxy
echo "Deploying Kong proxy..."
kubectl apply -f kong.yaml

# Wait for Kong to be ready
echo "Waiting for Kong to be ready..."
kubectl wait --for=condition=ready pod -l app=kong -n microservices-stack --timeout=120s || true

# Apply Envoy proxy (optional - keeping for backward compatibility)
echo "Deploying Envoy proxy (optional)..."
kubectl apply -f envoy-config.yaml
kubectl apply -f envoy.yaml

# Apply ingress (optional - requires ingress controller)
echo "Deploying ingress..."
kubectl apply -f ingress.yaml

echo "Deployment completed!"
echo ""
echo "Checking pod status..."
kubectl get pods -n microservices-stack

echo ""
echo "Pod status details (if any pods are not ready):"
kubectl get pods -n microservices-stack -o wide

echo ""
echo "Services:"
kubectl get services -n microservices-stack

echo ""
echo "=== Troubleshooting Commands ==="
echo "If pods are not ready, use these commands to diagnose:"
echo ""
echo "# Check pod events:"
echo "kubectl describe pod <pod-name> -n microservices-stack"
echo ""
echo "# Check pod logs:"
echo "kubectl logs <pod-name> -n microservices-stack"
echo ""
echo "# Check all users-service logs:"
echo "kubectl logs -l app=users-service -n microservices-stack --tail=50"
echo ""
echo "# Check all orders-service logs:"
echo "kubectl logs -l app=orders-service -n microservices-stack --tail=50"
echo ""

echo ""
echo "Access URLs via Kong Proxy:"
KONG_IP=$(kubectl get svc kong-proxy -n microservices-stack -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "")
KONG_HOST=$(kubectl get svc kong-proxy -n microservices-stack -o jsonpath='{.status.loadBalancer.ingress[0].hostname}' 2>/dev/null || echo "")

if [ -n "$KONG_IP" ]; then
  KONG_URL="http://$KONG_IP:8000"
elif [ -n "$KONG_HOST" ]; then
  KONG_URL="http://$KONG_HOST:8000"
else
  KONG_URL="http://localhost:8000 (use port-forward)"
fi

echo "- Kong Proxy: $KONG_URL"
echo "- Auth Service via Kong: $KONG_URL/api/v1/auth"
echo "- Orders Service via Kong: $KONG_URL/api/v1/orders"
echo "- Auth Health: $KONG_URL/auth/health"
echo "- Orders Health: $KONG_URL/orders/health"
echo ""
echo "Direct service access:"
echo "- Users Service: http://users-service.local"
echo "- Orders Service: http://orders-service.local"
echo "- Prometheus: http://prometheus.local"
echo "- Grafana: http://grafana.local (admin/admin)"
echo "- Alertmanager: http://alertmanager.local"
echo ""
echo "Port forwarding (if LoadBalancer not available):"
echo "kubectl port-forward svc/kong-proxy 8000:8000 -n microservices-stack"
echo "kubectl port-forward svc/kong-admin 8001:8001 -n microservices-stack"
echo "kubectl port-forward svc/envoy-proxy 8080:8080 -n microservices-stack"
echo "kubectl port-forward svc/envoy-proxy 9901:9901 -n microservices-stack"
echo "kubectl port-forward svc/users-service 8000:8000 -n microservices-stack"
echo "kubectl port-forward svc/orders-service 8001:8001 -n microservices-stack"
echo "kubectl port-forward svc/prometheus 9090:9090 -n microservices-stack"
echo "kubectl port-forward svc/grafana 3000:3000 -n microservices-stack"
echo "kubectl port-forward svc/alertmanager 9093:9093 -n microservices-stack"
