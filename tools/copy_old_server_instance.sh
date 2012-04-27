#!/bin/bash

FST_INSTANCE=$1
OLD_SERVER=$2
NEW_SERVER=rinfo@fst.lagrummet.se

echo fab prod create_instance:$FST_INSTANCE

OLD_INSTANCE_DIR=$OLD_SERVER:/opt/rinfo/fst/instances/$FST_INSTANCE
NEW_INSTANCE_DIR=$NEW_SERVER:/opt/rinfo/fst/instances/$FST_INSTANCE

echo scp $OLD_INSTANCE_DIR/fst_web/local_settings.py $NEW_INSTANCE_DIR/fst_web/
echo scp $OLD_INSTANCE_DIR/fst_web/database/fst*.db $NEW_INSTANCE_DIR/fst_web/database/
echo scp -r $OLD_INSTANCE_DIR/fst_web/uploads $NEW_INSTANCE_DIR/fst_web/

