## Overview
These protos have been copied and modified from the [official Helium repo](https://github.com/helium/proto).
That repo does not yet have a build process for Python. 
Eventually, we may want to manage all protos.
For the moment, we are just copying the files we absolutely need: 
`blockchain_txn_add_gateway_v1` and the wrapper transaction `blockchain_txn`.

## Generating protos

1. Install [protobuf](https://developers.google.com/protocol-buffers/docs/downloads)
2. Generate protos

```bash
SRC_DIR=/PATH/TO/hm-pyhelper/protos
DST_DIR=/PATH/TO/hm-pyhelper/hm_pyhelper/protos
protoc -I=$SRC_DIR --python_out=$DST_DIR $SRC_DIR/blockchain_txn.proto
protoc -I=$SRC_DIR --python_out=$DST_DIR $SRC_DIR/blockchain_txn_add_gateway_v1.proto
```

For frequently changing proto files, we use [this] (https://github.com/NebraLtd/hm-pyhelper/blob/master/protos/update_protos.sh) script to download and generate the python code.