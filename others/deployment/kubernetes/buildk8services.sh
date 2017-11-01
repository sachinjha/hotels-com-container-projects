kubectl create -f locationquery-service-deployment.yaml
kubectl create -f locationquery-service-service.yaml

kubectl create -f hotelquery-service-deployment.yaml
kubectl create -f hotelquery-service-service.yaml

kubectl create -f dealsquery-service-deployment.yaml
kubectl create -f dealsquery-service-service.yaml

kubectl create -f amenitiesquery-service-deployment.yaml
kubectl create -f amenitiesquery-service-service.yaml

kubectl create -f controller-deployment.yaml
kubectl create -f controller-service.yaml

kubectl create -f zipkin-deployment.yaml
kubectl create -f zipkin-service.yaml