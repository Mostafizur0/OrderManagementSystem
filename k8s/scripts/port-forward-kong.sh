#!/bin/bash
# Port-forward script for Kong Manager and Admin API

echo "Starting port-forwards for Kong Manager..."
echo "Kong Manager will be available at: http://localhost:8002"
echo "Admin API will be available at: http://localhost:8001"
echo ""
echo "Press Ctrl+C to stop all port-forwards"
echo ""

# Port-forward Kong Manager
kubectl port-forward svc/kong-manager 8002:8002 -n microservices-stack &
KONG_MANAGER_PID=$!

# Port-forward Admin API (needed for Kong Manager to work)
kubectl port-forward svc/kong-admin 8001:8001 -n microservices-stack &
KONG_ADMIN_PID=$!

# Wait for user interrupt
trap "kill $KONG_MANAGER_PID $KONG_ADMIN_PID 2>/dev/null; exit" INT TERM

wait
