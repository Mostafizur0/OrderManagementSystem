# Kubernetes Deployment for Microservices Stack

This directory contains Kubernetes manifests to deploy the complete microservices stack including:
- FastAPI Users Service (Auth)
- FastAPI Orders Service
- PostgreSQL database
- Kong API Gateway (Proxy for services)
- Prometheus monitoring
- Alertmanager alerting
- Grafana visualization
- Infrastructure monitoring (cAdvisor, Node Exporter)

## Architecture Overview

```
                    ┌─────────────────┐
                    │   Kong Gateway  │
                    │   (Port 8000)   │
                    └────────┬────────┘
                             │
          ┌──────────────────┴──────────────────┐
          │                                     │
┌─────────▼─────────┐              ┌───────────▼──────────┐
│   Users Service   │              │   Orders Service     │
│   (Port 8000)     │              │   (Port 8001)        │
│   (Auth)          │              │                      │
└─────────┬─────────┘              └───────────┬──────────┘
          │                                     │
          └──────────────┬──────────────────────┘
                         │
              ┌──────────▼──────────┐
              │    PostgreSQL       │
              │   (Port 5432)      │
              └─────────────────────┘

┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   Prometheus    │  │  Alertmanager   │  │     Grafana     │
│   (Port 9090)   │  │   (Port 9093)   │  │   (Port 3000)   │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

## Prerequisites

- Kubernetes cluster (local: minikube, kind, docker-desktop, or any K8s cluster)
- kubectl configured
- Docker installed
- Ingress controller (optional, for external access)

## Quick Start

### 1. Build Docker Images

```bash
cd k8s
./build-images.sh
```

### 2. Deploy to Kubernetes

```bash
./deploy.sh
```

### 3. Access Services

#### Option A: Via Kong Gateway (Recommended)

Kong Gateway provides a single entry point for all services. It's accessible via LoadBalancer (if supported) or port-forwarding:

```bash
# Get Kong service details
kubectl get svc kong-proxy -n microservices-stack

# If LoadBalancer is available, get the external IP
KONG_IP=$(kubectl get svc kong-proxy -n microservices-stack -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

# Or use port-forwarding (for Kind or local clusters)
kubectl port-forward svc/kong-proxy 8000:8000 -n microservices-stack
```

Then access services via Kong:
- **Auth Service**: `http://localhost:8000/api/v1/auth`
- **Orders Service**: `http://localhost:8000/api/v1/orders`
- **Auth Health**: `http://localhost:8000/auth/health`
- **Orders Health**: `http://localhost:8000/orders/health`
- **Kong Admin API**: `http://localhost:8001` (port-forward to kong-admin service)

#### Option B: Direct Port Forwarding

```bash
# Users Service
kubectl port-forward svc/users-service 8000:8000 -n microservices-stack

# Orders Service
kubectl port-forward svc/orders-service 8001:8001 -n microservices-stack

# Prometheus
kubectl port-forward svc/prometheus 9090:9090 -n microservices-stack

# Grafana (admin/admin)
kubectl port-forward svc/grafana 3000:3000 -n microservices-stack

# Alertmanager
kubectl port-forward svc/alertmanager 9093:9093 -n microservices-stack
```

#### Option B: Ingress (Requires Ingress Controller)

Add to your `/etc/hosts`:
```
127.0.0.1 users-service.local orders-service.local prometheus.local grafana.local alertmanager.local
```

Then access:
- Users Service: http://users-service.local
- Orders Service: http://orders-service.local
- Prometheus: http://prometheus.local
- Grafana: http://grafana.local (admin/admin)
- Alertmanager: http://alertmanager.local

## File Structure

```
k8s/
├── namespace.yaml              # Namespace and network policies
├── postgres.yaml               # PostgreSQL deployment and PVC
├── users-service.yaml          # Users service deployment
├── orders-service.yaml         # Orders service deployment
├── kong.yaml                   # Kong API Gateway deployment
├── monitoring-configmaps.yaml   # Prometheus and Alertmanager configs
├── prometheus.yaml             # Prometheus deployment
├── alertmanager.yaml           # Alertmanager deployment
├── grafana.yaml                # Grafana deployment
├── infrastructure.yaml         # cAdvisor and Node Exporter
├── ingress.yaml                # Ingress configuration
├── build-images.sh             # Script to build Docker images
├── deploy.sh                   # Script to deploy everything
└── README.md                   # This file
```

## Configuration

### Secrets

- **PostgreSQL**: Database credentials stored in `postgres-secret`
- **Grafana**: Admin credentials stored in `grafana-secret` (admin/admin)

### ConfigMaps

- **Users Service**: Environment variables including database URL
- **Orders Service**: Environment variables including database URL
- **Kong**: Declarative configuration for routes and services
- **Prometheus**: Monitoring configuration and alert rules
- **Alertmanager**: Alert routing configuration

### Resource Limits

All deployments include resource requests and limits:
- **Microservices**: 256Mi/512Mi memory, 250m/500m CPU
- **PostgreSQL**: 256Mi/512Mi memory, 250m/500m CPU
- **Prometheus**: 512Mi/1Gi memory, 500m/1CPU
- **Grafana**: 256Mi/512Mi memory, 250m/500m CPU

## Monitoring Stack

### Prometheus
- Scrape interval: 10 seconds
- Data retention: 200 hours
- Targets: Both microservices, infrastructure components

### Alertmanager
- Discord integration configured
- Group alerts by alertname and job
- 30s group wait, 5m group interval, 3h repeat interval

### Grafana
- Admin access: admin/admin
- Anonymous access enabled for development
- Pre-configured to connect to Prometheus

## Health Checks

All services include:
- **Liveness probes**: Detect if service is running
- **Readiness probes**: Detect if service is ready to accept traffic
- **Health endpoints**: `/health` for microservices, `/-/healthy` for monitoring components

## Storage

Persistent storage is configured for:
- **PostgreSQL**: 5Gi for database data
- **Prometheus**: 10Gi for metrics data
- **Alertmanager**: 2Gi for alert data
- **Grafana**: 5Gi for dashboards and configuration

## Scaling

- **Microservices**: Configured with 2 replicas (can be scaled horizontally)
- **Database**: Single instance (consider external database for production)
- **Monitoring**: Single instances (sufficient for most use cases)

## Kong API Gateway

Kong is configured in DB-less mode with declarative configuration. It provides:

- **Single entry point**: All services accessible through Kong
- **Route management**: Routes requests to appropriate services
- **Load balancing**: Distributes traffic across service replicas
- **External access**: LoadBalancer service type for external access (works with MetalLB on Kind)

### Kong Routes

- `/api/v1/auth/*` → Users Service (Auth endpoints)
- `/api/v1/orders/*` → Orders Service
- `/auth/health` → Users Service health check
- `/orders/health` → Orders Service health check

### Accessing Kong

For Kind clusters, you may need to:
1. Install MetalLB for LoadBalancer support, OR
2. Use port-forwarding: `kubectl port-forward svc/kong-proxy 8000:8000 -n microservices-stack`

### Kong Requirements

For detailed requirements and setup instructions, see [KONG_REQUIREMENTS.md](KONG_REQUIREMENTS.md)

**Quick Summary:**
- ✅ No database required (DB-less mode)
- ✅ Works with Kind, Minikube, Docker Desktop
- ✅ Minimum: 2 CPU cores, 4GB RAM
- ✅ Network: MetalLB (recommended) or port-forwarding

## Network Security

- **Namespace isolation**: All services in dedicated namespace
- **Network policies**: Restrict traffic between namespaces
- **Service mesh ready**: Can integrate with Istio or Linkerd
- **API Gateway**: Kong provides centralized API management

## Troubleshooting

### Check Pod Status
```bash
kubectl get pods -n microservices-stack
kubectl describe pod <pod-name> -n microservices-stack
```

### Check Logs
```bash
kubectl logs <pod-name> -n microservices-stack -f
```

### Port Forwarding Issues
If port forwarding doesn't work, check:
1. Pod is running: `kubectl get pods -n microservices-stack`
2. Service exists: `kubectl get svc -n microservices-stack`
3. Port is not already in use

### Storage Issues
For local clusters, ensure storage class is available:
```bash
kubectl get storageclass
```

## Production Considerations

For production deployment, consider:
1. **External database**: Use managed PostgreSQL service
2. **Resource limits**: Adjust based on actual usage
3. **SSL/TLS**: Enable HTTPS for all services
4. **Backup strategy**: Implement database and configuration backups
5. **Monitoring alerts**: Configure appropriate alert thresholds
6. **High availability**: Deploy multiple replicas with anti-affinity rules

## Cleanup

To remove the entire stack:
```bash
kubectl delete namespace microservices-stack
```

This will remove all resources in the namespace.
