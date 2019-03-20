protoc -I=./protos --python_out=./remme/protos ./protos/*.proto
sed -i "s/^import \([^ ]*\)_pb2 as \([^ ]*\)$/import remme.protos.\1_pb2 as \2/" remme/protos/*_pb2.py