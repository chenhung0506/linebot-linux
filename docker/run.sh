#!/bin/bash
# REPO=docker-reg.emotibot.com.cn:55688
#this is git test
WORK_PATH=$(dirname "$0")
source ${WORK_PATH}/build.sh 
REPO=chenhung0506
CONTAINER=linebot-linux
exprot $REPO
exprot $CONTAINER

export TAG=$(git rev-parse --short HEAD)
set -o allexport
source ../module/dev.env
set +o allexport

echo "[ -------- 0.   build/push base image -------- ]"
echo "[ -------- 1.   build and run         -------- ]"
echo "[ -------- 2.   pull image and run    -------- ]"
echo "[ -------- 3.   run module            -------- ]"
echo "[ -------- 4.   stop module           -------- ]"
echo "[ -------- 5.   save image            -------- ]"
echo "[ -------- 6.   save deploy           -------- ]"

if [ $# -eq 1 ]; then
    input_str=$1
else
    read input_str
fi

echo "input_str:"$input_str
CMD=""

operation() {
    mode=$1
    if [ $mode == "0" ]; then
        CMD=("build_base_image")
        for i in "${CMD[@]}";do
            echo $i
        done
    elif [ $mode == "1" ]; then
        CMD=("build" "dockerComposeUp")
        for i in "${CMD[@]}";do
            echo $i
        done
    elif [ $mode == "2" ]; then
        CMD=("imagePull" "dockerComposeUp")
        for i in "${CMD[@]}";do
            echo $i
        done
    elif [ $mode == "3" ]; then
        read -p "Enter TAG: " INPUT_TAG
        # echo "input TAG: $INPUT_TAG"
        export TAG=$INPUT_TAG
        CMD=("docker-compose up -d")
        for i in "${CMD[@]}";do
            echo $i
        done
    elif [ $mode == "4" ]; then
        CMD=("docker-compose down")
        for i in "${CMD[@]}";do
            echo $i
        done
    elif [ $mode == "5" ]; then
        CMD=("saveImage")
        for i in "${CMD[@]}";do
            echo $i
        done
    elif [ $mode == "6" ]; then
        CMD=("saveDeploy")
        for i in "${CMD[@]}";do
            echo $i
        done
    fi
}

execute_iterator(){
    if [[ ${#input_str} > 0 ]]; then
        input_arr=($(echo $input_str | sed  's/,/ /g'))
        for i in "${input_arr[@]}";do
            local res=$(operation $i)
            res_arr=($(echo $res | sed  's/ / /g'))
            for i in "${res_arr[@]}";do
                echo $i && eval $i
            done
            # for j in "${res[@]}";do
            #     echo "::::"
            #     echo "::::"
            #     echo $j && eval $j
            # done
        done
    fi
}

execute_iterator
# execute