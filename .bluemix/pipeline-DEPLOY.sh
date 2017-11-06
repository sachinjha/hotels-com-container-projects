#!/bin/bash
#set -x
#Check cluster availability
ip_addr=$(bx cs workers $PIPELINE_KUBERNETES_CLUSTER_NAME | grep normal | awk '{ print $2 }')
if [ -z $ip_addr ]; then
echo "$PIPELINE_KUBERNETES_CLUSTER_NAME not created or workers not ready"
exit 1
fi

cd others/deployment/kubernetes/bxkube

kubectl apply -f locationquery-deployment.yaml
kubectl apply -f locationquery-service-service.yaml

kubectl apply -f hotelquery-deployment.yaml
kubectl apply -f hotelquery-service-service.yaml

kubectl apply -f dealsquery-deployment.yaml
kubectl apply -f dealsquery-service-service.yaml

kubectl apply -f amenitiesquery-deployment.yaml
kubectl apply -f amenitiesquery-service-service.yaml

kubectl apply -f controller-deployment.yaml
kubectl apply -f controller-service.yaml

kubectl apply -f zipkin-deployment.yaml
kubectl apply -f zipkin-service.yaml

kubectl get services

CONTROLLER_CLUSTER_IP=`kubectl get services/controller -o=jsonpath="{.spec.clusterIP}"`

# install yaml
if [ ! -f ./yaml ]; then
    wget https://github.com/mikefarah/yaml/releases/download/1.5/yaml_linux_amd64 -O yaml
    chmod +x yaml
fi

./yaml w --inplace ui-deployment.yaml spec.template.spec.containers.env[1].value "http://${CONTROLLER_CLUSTER_IP}:31101"
cat  definitions/onboarding-event-api.yaml

kubectl apply -f ui-deployment.yaml
kubectl apply -f ui-service.yaml

kubectl describe services
