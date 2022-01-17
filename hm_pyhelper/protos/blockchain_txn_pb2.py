# flake8: noqa
# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: blockchain_txn.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


import hm_pyhelper.protos.blockchain_txn_add_gateway_v1_pb2 as blockchain__txn__add__gateway__v1__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='blockchain_txn.proto',
  package='helium',
  syntax='proto3',
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\n\x14\x62lockchain_txn.proto\x12\x06helium\x1a#blockchain_txn_add_gateway_v1.proto\"U\n\x0e\x62lockchain_txn\x12<\n\x0b\x61\x64\x64_gateway\x18\x01 \x01(\x0b\x32%.helium.blockchain_txn_add_gateway_v1H\x00\x42\x05\n\x03txnb\x06proto3'
  ,
  dependencies=[blockchain__txn__add__gateway__v1__pb2.DESCRIPTOR,])




_BLOCKCHAIN_TXN = _descriptor.Descriptor(
  name='blockchain_txn',
  full_name='helium.blockchain_txn',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='add_gateway', full_name='helium.blockchain_txn.add_gateway', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
    _descriptor.OneofDescriptor(
      name='txn', full_name='helium.blockchain_txn.txn',
      index=0, containing_type=None,
      create_key=_descriptor._internal_create_key,
    fields=[]),
  ],
  serialized_start=69,
  serialized_end=154,
)

_BLOCKCHAIN_TXN.fields_by_name['add_gateway'].message_type = blockchain__txn__add__gateway__v1__pb2._BLOCKCHAIN_TXN_ADD_GATEWAY_V1
_BLOCKCHAIN_TXN.oneofs_by_name['txn'].fields.append(
  _BLOCKCHAIN_TXN.fields_by_name['add_gateway'])
_BLOCKCHAIN_TXN.fields_by_name['add_gateway'].containing_oneof = _BLOCKCHAIN_TXN.oneofs_by_name['txn']
DESCRIPTOR.message_types_by_name['blockchain_txn'] = _BLOCKCHAIN_TXN
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

blockchain_txn = _reflection.GeneratedProtocolMessageType('blockchain_txn', (_message.Message,), {
  'DESCRIPTOR' : _BLOCKCHAIN_TXN,
  '__module__' : 'blockchain_txn_pb2'
  # @@protoc_insertion_point(class_scope:helium.blockchain_txn)
  })
_sym_db.RegisterMessage(blockchain_txn)


# @@protoc_insertion_point(module_scope)
