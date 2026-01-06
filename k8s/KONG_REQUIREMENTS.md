# Kong API Gateway - Local Cluster Requirements

This document outlines the requirements and setup needed to run Kong API Gateway in a local Kubernetes cluster (Kind, Minikube, Docker Desktop, etc.).

## Prerequisites

### 1. Kubernetes Cluster
- **Kind** (Kubernetes in Docker) - Recommended for local development
- **Minikube** - Alternative local cluster option
- **Docker Desktop** - Built-in Kubernetes support
- **K3s/K3d** - Lightweight Kubernetes distribution

**Minimum Requirements:**
- Kubernetes version: 1.19+ (recommended: 1.24+)
- At least 1 node with 2 CPU cores and 4GB RAM available

### 2. Command Line Tools
- **kubectl** - Kubernetes command-line tool (configured to access your cluster)
- **Docker** - For building images and running Kind clusters

### 3. System Resources
- **CPU**: Minimum 2 cores (4+ recommended)
- **RAM**: Minimum 4GB available (8GB+ recommended)
- **Disk**: At least 10GB free space for images and storage

## Kong-Specific Requirements

### 1. Kong Deployment Mode

Our setup uses **DB-less mode** (declarative configuration), which means:

✅ **No Database Required**
- Kong runs without PostgreSQL or Cassandra
- Configuration is loaded from a ConfigMap (declarative YAML)
- Simpler setup, no database migrations needed
- Perfect for local development and testing

❌ **Not Required:**
- PostgreSQL database
- Database migrations
- Database connection configuration
- Persistent storage for Kong

### 2. Kong Image
- **Image**: `kong:3.4` (or latest stable version)
- **Image Size**: ~200MB
- **Pull Policy**: `IfNotPresent` (uses local image if available)

### 3. Resource Requirements

**Per Kong Pod:**
- **Memory**: 
  - Request: 512Mi
  - Limit: 1Gi (required for Kong 3.4)
- **CPU**:
  - Request: 250m (0.25 cores)
  - Limit: 500m (0.5 cores)

**Total for 2 Replicas:**
- Memory: ~1Gi - 2Gi
- CPU: ~0.5 - 1 core

**Note**: Kong 3.4 requires at least 1Gi memory per pod due to multiple worker processes. The configuration limits workers to 2 processes to reduce memory usage.

### 4. Network Requirements

#### Ports Used by Kong:
- **8000**: Proxy port (main API gateway)
- **8001**: Admin API port (management)
- **8443**: Proxy SSL port (HTTPS, optional)
- **8444**: Admin SSL port (HTTPS, optional)

#### Network Access:
- **Internal**: Kong can access services within the cluster via ClusterIP services
- **External**: Requires LoadBalancer support or port-forwarding

## Local Cluster Networking Options

### Option 1: LoadBalancer with MetalLB (Recommended for Kind)

**Requirements:**
- MetalLB installed in your Kind cluster
- IP address pool configured

**Installation:**
```bash
# Install MetalLB
kubectl apply -f https://raw.githubusercontent.com/metallb/metallb/v0.13.12/config/manifests/metallb-native.yaml

# Wait for MetalLB to be ready
kubectl wait --namespace metallb-system \
  --for=condition=ready pod \
  --selector=app=metallb \
  --timeout=90s

# Configure IP pool (adjust IP range for your network)
cat <<EOF | kubectl apply -f -
apiVersion: metallb.io/v1beta1
kind: IPAddressPool
metadata:
  name: default-pool
  namespace: metallb-system
spec:
  addresses:
  - 172.18.255.200-172.18.255.250
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
```

**Benefits:**
- Kong gets a real external IP
- Accessible from host machine and other devices on network
- No port-forwarding needed

### Option 2: Port Forwarding (Simplest, No Setup)

**Requirements:**
- kubectl configured
- No additional setup needed

**Usage:**
```bash
# Forward Kong proxy port
kubectl port-forward svc/kong-proxy 8000:8000 -n microservices-stack

# Forward Kong admin port (optional)
kubectl port-forward svc/kong-admin 8001:8001 -n microservices-stack
```

**Benefits:**
- Works immediately, no setup
- Good for development and testing
- Accessible at `localhost:8000`

**Limitations:**
- Only accessible from local machine
- Requires active port-forward session
- Not suitable for production-like testing

### Option 3: NodePort Service

**Requirements:**
- Modify Kong service type to NodePort
- Access via `<node-ip>:<nodeport>`

**Modification:**
Change `type: LoadBalancer` to `type: NodePort` in `kong.yaml`

**Benefits:**
- Accessible without port-forwarding
- Works on all local cluster types

**Limitations:**
- Requires finding node IP
- Port may be high-numbered (30000+)

### Option 4: Ingress Controller

**Requirements:**
- Ingress controller installed (NGINX, Traefik, etc.)
- Ingress resource configured

**Benefits:**
- Standard Kubernetes approach
- Can use hostnames with `/etc/hosts`

## Configuration Requirements

### 1. Kong Configuration File

**Location**: `k8s/kong.yaml` (ConfigMap)

**Key Settings:**
- `KONG_DATABASE: "off"` - DB-less mode
- `KONG_DECLARATIVE_CONFIG: "/kong/kong.yml"` - Config file path
- Routes and services defined in declarative YAML

### 2. Service Discovery

Kong needs to reach backend services:
- **Auth Service**: `http://users-service:8000`
- **Orders Service**: `http://orders-service:8001`

**Requirements:**
- Services must be in the same namespace or accessible via DNS
- Services must have ClusterIP or be accessible within cluster

### 3. Network Policies

Current network policy allows:
- Traffic within `microservices-stack` namespace
- Kong can access services on ports 8000, 8001

## Health Checks

Kong includes health check endpoints:
- **Liveness**: `/status` on admin port (8001)
- **Readiness**: `/status` on admin port (8001)

**Probe Configuration:**
- Initial delay: 30s (liveness), 5s (readiness)
- Period: 10s
- Timeout: 5s
- Failure threshold: 3

## Storage Requirements

**No Persistent Storage Needed:**
- Kong in DB-less mode doesn't require persistent volumes
- Configuration is stored in ConfigMap (ephemeral)
- Logs go to stdout/stderr (collected by logging system)

## Quick Setup Checklist

- [ ] Kubernetes cluster running (Kind/Minikube/etc.)
- [ ] kubectl configured and working
- [ ] Docker installed and running
- [ ] Services (users-service, orders-service) deployed
- [ ] Kong deployment applied (`kubectl apply -f kong.yaml`)
- [ ] Kong pods running (`kubectl get pods -n microservices-stack`)
- [ ] Network access configured (MetalLB, port-forward, or NodePort)
- [ ] Test access: `curl http://localhost:8000/api/v1/auth/health`

## Troubleshooting

### Kong Pods Not Starting
```bash
# Check pod status
kubectl get pods -l app=kong -n microservices-stack

# Check logs
kubectl logs -l app=kong -n microservices-stack

# Check events
kubectl describe pod <kong-pod-name> -n microservices-stack
```

### Cannot Access Kong
```bash
# Check service
kubectl get svc kong-proxy -n microservices-stack

# Check if LoadBalancer has external IP
kubectl get svc kong-proxy -n microservices-stack -o wide

# If no external IP, use port-forward
kubectl port-forward svc/kong-proxy 8000:8000 -n microservices-stack
```

### Routes Not Working
```bash
# Check Kong configuration
kubectl get configmap kong-config -n microservices-stack -o yaml

# Check Kong admin API
kubectl port-forward svc/kong-admin 8001:8001 -n microservices-stack
curl http://localhost:8001/services
curl http://localhost:8001/routes
```

## Production Considerations

For production deployments, consider:
1. **Database Mode**: Use PostgreSQL for dynamic configuration
2. **High Availability**: Multiple replicas across nodes
3. **Resource Limits**: Adjust based on traffic
4. **SSL/TLS**: Enable HTTPS endpoints
5. **Monitoring**: Integrate with Prometheus/Grafana
6. **Backup**: Backup Kong configuration
7. **Security**: Enable authentication for admin API

## Summary

**Minimum Requirements:**
- Kubernetes cluster (1.19+)
- kubectl configured
- 2 CPU cores, 4GB RAM
- Kong image (`kong:3.4`)
- No database needed (DB-less mode)

**Recommended Setup:**
- Kind cluster with MetalLB
- 4+ CPU cores, 8GB RAM
- Port-forwarding for quick access
- Monitoring enabled

**Current Configuration:**
- ✅ DB-less mode (no database)
- ✅ 2 replicas for high availability
- ✅ LoadBalancer service (works with MetalLB)
- ✅ Declarative configuration via ConfigMap
- ✅ Health checks configured
- ✅ Resource limits set

