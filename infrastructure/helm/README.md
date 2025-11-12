# FinCloud Helm Chart

Helm chart for deploying FinCloud to Kubernetes.

## Prerequisites

- Kubernetes 1.20+
- Helm 3+
- cert-manager (for TLS)
- nginx-ingress-controller

## Installation

```bash
# Add the Helm repository
helm repo add fincloud https://your-org.github.io/FinCloud

# Update repositories
helm repo update

# Install FinCloud
helm install fincloud fincloud/fincloud \
  --namespace fincloud \
  --create-namespace \
  --values custom-values.yaml
```

## Configuration

See `values.yaml` for all configuration options.

### Basic Configuration

```yaml
# custom-values.yaml
postgresql:
  auth:
    password: "your-secure-password"

minio:
  auth:
    rootPassword: "your-secure-password"

ingress:
  hosts:
    - host: fincloud.yourdomain.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: fincloud-tls
      hosts:
        - fincloud.yourdomain.com
```

## Upgrade

```bash
helm upgrade fincloud fincloud/fincloud \
  --namespace fincloud \
  --values custom-values.yaml
```

## Uninstall

```bash
helm uninstall fincloud --namespace fincloud
```

## Development

```bash
# Lint the chart
helm lint .

# Template and validate
helm template fincloud . --values values.yaml

# Install from local directory
helm install fincloud . --namespace fincloud --create-namespace
```
