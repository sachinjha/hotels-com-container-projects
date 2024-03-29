#!/bin/bash
#set -x
echo "REGISTRY_URL=${REGISTRY_URL}"
echo "REGISTRY_NAMESPACE=${REGISTRY_NAMESPACE}"
echo "IMAGE_NAME=${IMAGE_NAME}"
echo "BUILD_NUMBER=${BUILD_NUMBER}"
echo "ARCHIVE_DIR=${ARCHIVE_DIR}"

# Learn more about the available environment variables at:
# https://console.bluemix.net/docs/services/ContinuousDelivery/pipeline_deploy_var.html#deliverypipeline_environment

# To review or change build options use:
# bx cr build --help

if [ -z ${REGISTRY_URL} ]; then
REGISTRY_URL="registry.ng.bluemix.net"
fi

echo "=========================================================="
echo "Checking registry current plan and quota"
bx cr plan
bx cr quota
echo "If needed, discard older images using: bx cr image-rm"

echo "Checking registry namespace: ${REGISTRY_NAMESPACE}"
NS=$( bx cr namespaces | grep ${REGISTRY_NAMESPACE} ||: )
if [ -z ${NS} ]; then
    echo "Registry namespace ${REGISTRY_NAMESPACE} not found, creating it."
    bx cr namespace-add ${REGISTRY_NAMESPACE}
    echo "Registry namespace ${REGISTRY_NAMESPACE} created."
else 
    echo "Registry namespace ${REGISTRY_NAMESPACE} found."
fi

echo -e "Existing images in registry"
bx cr images
PARENT_DIR=../others/deployment/kubernetes/bxkube
for dir in amenitiesquery	controller	dealsquery hotelquery	locationquery	ui; do 
    pushd $dir
    IMAGE_NAME=hotels-${dir}
    echo "=========================================================="
    echo "Inside $dir"
    echo "Checking for Dockerfile at the repository root"
    if [ -f Dockerfile ]; then 
        echo "Dockerfile found"
    else
        echo "Dockerfile not found"
        exit 1
    fi

    
    echo "=========================================================="
    echo -e "Building container image: ${IMAGE_NAME}:${BUILD_NUMBER}"
    IMAGE_LOCATION=${REGISTRY_URL}/${REGISTRY_NAMESPACE}/${IMAGE_NAME}
    set -x
    bx cr build -t ${IMAGE_LOCATION}:${BUILD_NUMBER} .
    set +x
    bx cr image-inspect ${IMAGE_LOCATION}:${BUILD_NUMBER}

    # IMAGE_NAME from build.properties is used by Vulnerability Advisor job to reference the image qualified location in registry
    echo "IMAGE_NAME=${IMAGE_LOCATION}:${BUILD_NUMBER}" >> $ARCHIVE_DIR/build.properties

    #Update deployment.yml with image name
    if [ -f ${PARENT_DIR}/${dir}-deployment.yaml ]; then
        echo "UPDATING DEPLOYMENT MANIFEST:"
        sed -i "s~^\([[:blank:]]*\)image:.*$~\1image: ${IMAGE_LOCATION}:${BUILD_NUMBER}~" ${PARENT_DIR}/${dir}-deployment.yaml
        cat ${PARENT_DIR}/${dir}-deployment.yaml 
    else 
        echo -e "${red}Deployment file' not found at ${PARENT_DIR}/${dir}-deployment.yaml ${no_color}"
        exit 1
    fi
    popd 

done