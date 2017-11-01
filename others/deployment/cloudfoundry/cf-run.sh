cf api https://api.ng.bluemix.net
cf login -o "Aruns Organization" -s hotels.com

cd ../..
cd locationquery 
cf push

cd ..
cd hotelquery
cf push

cd ..
cd controller
cf push
