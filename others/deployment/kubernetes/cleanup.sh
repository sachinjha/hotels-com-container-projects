kubectl delete pv redispv
kubectl delete pv mysqlpv
kubectl delete pv imagespv

kubectl delete pvc redis-claim0
kubectl delete pvc mysql-claim0
kubectl delete pvc images-claim0

kubectl delete deployment locationquery-service
kubectl delete deployment hotelquery-service
kubectl delete deployment dealsquery-service
kubectl delete deployment amenitiesquery-service
kubectl delete deployment controller
kubectl delete deployment zipkin

kubectl delete service locationquery-service
kubectl delete service hotelquery-service
kubectl delete service dealsquery-service
kubectl delete service amenitiesquery-service
kubectl delete service controller
kubectl delete service zipkin
