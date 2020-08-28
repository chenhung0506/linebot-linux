#!/bin/bash
build() {
  TAG=$(git rev-parse --short HEAD)
  DOCKER_IMAGE=$REPO/$CONTAINER:$TAG

  DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
  BUILDROOT=$DIR/..

  # Build docker
  cmd="DOCKER_BUILDKIT=1 docker build -t $DOCKER_IMAGE -f $DIR/Dockerfile $BUILDROOT --no-cache=true"
  echo $cmd
  eval $cmd
}

build_base_image() {
  echo "docker build -t python-with-chrome -f ./build_from_image/Dockerfile . "
  eval "docker build -t python-with-chrome -f ./build_from_image/Dockerfile . "
  echo "docker tag python-with-chrome:latest chenhung0506/python-with-chrome"
  eval "docker tag python-with-chrome:latest chenhung0506/python-with-chrome"
  echo "docker push chenhung0506/python-with-chrome:latest"
  eval "docker push chenhung0506/python-with-chrome:latest"
}

imagePush() {
  REPO=chenhung0506
  CONTAINER=linebot
  TAG=$(git rev-parse --short HEAD)
  DOCKER_IMAGE=$REPO/$CONTAINER:$TAG
  docker push DOCKER_IMAGE
}

imagePull() {
    TAG=$(git rev-parse --short HEAD)
    DOCKER_IMAGE=$REPO/$CONTAINER:$TAG
    echo "# Launching $DOCKER_IMAGE"
    # Check if docker image exists (locally or on the registry)
    local_img=$(docker images | grep $REPO | grep $CONTAINER | grep $TAG)
    if [ -z "$local_img" ] ; then
      echo "# Image not found locally, let's try to pull it from the registry."
      docker pull $DOCKER_IMAGE
      if [ "$?" -ne 0 ]; then
        echo "# Error: Image not found: $DOCKER_IMAGE"
        exit 1
      fi
    fi
    echo "# Great! Docker image found: $DOCKER_IMAGE"
}

dockerComposeUp() {
  cmd="docker-compose up -d"
  echo $cmd
  eval $cmd
}

dockerRun() {
  global config:" \
  - use local timezone \
  - max memory = 5G \
  "
  globalConf="
    -v /etc/localtime:/etc/localtime \
    -m 5125m \
    --restart always \
    --net docker-compose-base_default \
  "
  moduleConf="
    -p $PORT:$PORT \
    --env-file $envfile \
  "
  docker rm -f -v $CONTAINER
  cmd="docker run -d --name $CONTAINER \
    $globalConf \
    $moduleConf \
    $DOCKER_IMAGE \
  "
  echo $cmd
  eval $cmd
}

saveImage(){
  TAG=$(git rev-parse --short HEAD)
  DOCKER_IMAGE=$REPO/$CONTAINER:$TAG
  DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
  BUILDROOT=$DIR/..

  if [ ! -e $BUILDROOT/imgs ]; then
    echo 'imgs folder not found mkdir it'
    mkdir $BUILDROOT/imgs
  fi

  cmd="docker save $DOCKER_IMAGE | gzip > $BUILDROOT/imgs/$CONTAINER-$TAG-$(date +"%Y%m%d%H%M%S").tar.gz"
  echo $cmd
  eval $cmd
}

saveDeploy(){
  TAG=$(git rev-parse --short HEAD)
  DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && cd .. && pwd )"
  PROJECT_NAME="$(cd $DIR && basename "$PWD")"
  BUILD_DIR=$DIR/../..
  cmd="tar -C $DIR/.. -zcvf ${DIR}-${TAG}.tar.gz ${PROJECT_NAME}"
  # $(basename "$PWD")
  echo $cmd
  eval $cmd
}