#!/bin/bash

SRC_DIR=.
DST_DIR=../hm_pyhelper/protos

function update_proto() {
    echo "Updating $1"
    wget $1

    # replace old if succcessful
    if [[ $? -eq 0 ]]; then
        mv $2.1 $2
    fi
}

update_proto https://raw.githubusercontent.com/helium/proto/master/src/service/local.proto local.proto
update_proto https://raw.githubusercontent.com/helium/proto/master/src/region.proto region.proto

python -m grpc_tools.protoc -I=$SRC_DIR --python_out=$DST_DIR $SRC_DIR/region.proto
python -m grpc_tools.protoc -I=$SRC_DIR --python_out=$DST_DIR --grpc_python_out=$DST_DIR $SRC_DIR/local.proto

sed -i -e 's/import *local_pb2/import hm_pyhelper.protos.local_pb2/' $DST_DIR/local_pb2_grpc.py
