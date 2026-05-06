# Troubleshooting

Common issues and solutions for DClaw Risk.

## Quick Diagnostics

```bash
# Check app pods
kubectl get pods -n dclaw-risk

# Check logs
kubectl logs -n dclaw-risk deployment/dclaw-risk-backend

# Check database
kubectl get clusters -n dclaw-risk
```

## Sections

- [Common Issues](./common-issues)
- [FAQ](./faq)
