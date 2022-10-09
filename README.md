# ms-mock
Mock microservices application

## Istio service mesh installation

Install Istio on the cluster
```bash
istioctl install --set profile=demo -y
```

enable sidecar injection
```bash
kubectl label namespace default istio-injection=enabled
```

## Deployment

```bash
skaffold run
```

The application is now accessible through the `istio-ingressgateway` service.
To get the external IP run

```bash
kubectl get service istio-ingressgateway -n istio-system
```