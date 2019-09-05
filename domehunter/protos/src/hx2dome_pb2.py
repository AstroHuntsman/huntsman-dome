# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: hx2dome.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='hx2dome.proto',
  package='hx2dome',
  syntax='proto3',
  serialized_options=None,
  serialized_pb=_b('\n\rhx2dome.proto\x12\x07hx2dome\"!\n\nReturnCode\x12\x13\n\x0breturn_code\x18\x01 \x01(\x05\"3\n\x04\x41zEl\x12\x13\n\x0breturn_code\x18\x01 \x01(\x05\x12\n\n\x02\x61z\x18\x02 \x01(\x01\x12\n\n\x02\x65l\x18\x03 \x01(\x01\"6\n\nIsComplete\x12\x13\n\x0breturn_code\x18\x01 \x01(\x05\x12\x13\n\x0bis_complete\x18\x02 \x01(\x08\"#\n\x0b\x42\x61sicString\x12\x14\n\x0c\x62\x61sic_string\x18\x01 \x01(\t\"\x07\n\x05\x45mpty2\x96\t\n\x07HX2Dome\x12.\n\x0b\x64\x61piGetAzEl\x12\x0e.hx2dome.Empty\x1a\r.hx2dome.AzEl\"\x00\x12\x34\n\x0c\x64\x61piGotoAzEl\x12\r.hx2dome.AzEl\x1a\x13.hx2dome.ReturnCode\"\x00\x12\x32\n\tdapiAbort\x12\x0e.hx2dome.Empty\x1a\x13.hx2dome.ReturnCode\"\x00\x12\x31\n\x08\x64\x61piOpen\x12\x0e.hx2dome.Empty\x1a\x13.hx2dome.ReturnCode\"\x00\x12\x32\n\tdapiClose\x12\x0e.hx2dome.Empty\x1a\x13.hx2dome.ReturnCode\"\x00\x12\x31\n\x08\x64\x61piPark\x12\x0e.hx2dome.Empty\x1a\x13.hx2dome.ReturnCode\"\x00\x12\x33\n\ndapiUnpark\x12\x0e.hx2dome.Empty\x1a\x13.hx2dome.ReturnCode\"\x00\x12\x35\n\x0c\x64\x61piFindHome\x12\x0e.hx2dome.Empty\x1a\x13.hx2dome.ReturnCode\"\x00\x12;\n\x12\x64\x61piIsGotoComplete\x12\x0e.hx2dome.Empty\x1a\x13.hx2dome.IsComplete\"\x00\x12;\n\x12\x64\x61piIsOpenComplete\x12\x0e.hx2dome.Empty\x1a\x13.hx2dome.IsComplete\"\x00\x12<\n\x13\x64\x61piIsCloseComplete\x12\x0e.hx2dome.Empty\x1a\x13.hx2dome.IsComplete\"\x00\x12;\n\x12\x64\x61piIsParkComplete\x12\x0e.hx2dome.Empty\x1a\x13.hx2dome.IsComplete\"\x00\x12=\n\x14\x64\x61piIsUnparkComplete\x12\x0e.hx2dome.Empty\x1a\x13.hx2dome.IsComplete\"\x00\x12?\n\x16\x64\x61piIsFindHomeComplete\x12\x0e.hx2dome.Empty\x1a\x13.hx2dome.IsComplete\"\x00\x12\x30\n\x08\x64\x61piSync\x12\r.hx2dome.AzEl\x1a\x13.hx2dome.ReturnCode\"\x00\x12=\n\x13\x64\x65viceInfoNameShort\x12\x0e.hx2dome.Empty\x1a\x14.hx2dome.BasicString\"\x00\x12<\n\x12\x64\x65viceInfoNameLong\x12\x0e.hx2dome.Empty\x1a\x14.hx2dome.BasicString\"\x00\x12G\n\x1d\x64\x65viceInfoDetailedDescription\x12\x0e.hx2dome.Empty\x1a\x14.hx2dome.BasicString\"\x00\x12\x43\n\x19\x64\x65viceInfoFirmwareVersion\x12\x0e.hx2dome.Empty\x1a\x14.hx2dome.BasicString\"\x00\x12\x39\n\x0f\x64\x65viceInfoModel\x12\x0e.hx2dome.Empty\x1a\x14.hx2dome.BasicString\"\x00\x62\x06proto3')
)




_RETURNCODE = _descriptor.Descriptor(
  name='ReturnCode',
  full_name='hx2dome.ReturnCode',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='return_code', full_name='hx2dome.ReturnCode.return_code', index=0,
      number=1, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
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
  ],
  serialized_start=26,
  serialized_end=59,
)


_AZEL = _descriptor.Descriptor(
  name='AzEl',
  full_name='hx2dome.AzEl',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='return_code', full_name='hx2dome.AzEl.return_code', index=0,
      number=1, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='az', full_name='hx2dome.AzEl.az', index=1,
      number=2, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='el', full_name='hx2dome.AzEl.el', index=2,
      number=3, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
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
  ],
  serialized_start=61,
  serialized_end=112,
)


_ISCOMPLETE = _descriptor.Descriptor(
  name='IsComplete',
  full_name='hx2dome.IsComplete',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='return_code', full_name='hx2dome.IsComplete.return_code', index=0,
      number=1, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='is_complete', full_name='hx2dome.IsComplete.is_complete', index=1,
      number=2, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
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
  ],
  serialized_start=114,
  serialized_end=168,
)


_BASICSTRING = _descriptor.Descriptor(
  name='BasicString',
  full_name='hx2dome.BasicString',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='basic_string', full_name='hx2dome.BasicString.basic_string', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
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
  ],
  serialized_start=170,
  serialized_end=205,
)


_EMPTY = _descriptor.Descriptor(
  name='Empty',
  full_name='hx2dome.Empty',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
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
  ],
  serialized_start=207,
  serialized_end=214,
)

DESCRIPTOR.message_types_by_name['ReturnCode'] = _RETURNCODE
DESCRIPTOR.message_types_by_name['AzEl'] = _AZEL
DESCRIPTOR.message_types_by_name['IsComplete'] = _ISCOMPLETE
DESCRIPTOR.message_types_by_name['BasicString'] = _BASICSTRING
DESCRIPTOR.message_types_by_name['Empty'] = _EMPTY
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

ReturnCode = _reflection.GeneratedProtocolMessageType('ReturnCode', (_message.Message,), dict(
  DESCRIPTOR = _RETURNCODE,
  __module__ = 'hx2dome_pb2'
  # @@protoc_insertion_point(class_scope:hx2dome.ReturnCode)
  ))
_sym_db.RegisterMessage(ReturnCode)

AzEl = _reflection.GeneratedProtocolMessageType('AzEl', (_message.Message,), dict(
  DESCRIPTOR = _AZEL,
  __module__ = 'hx2dome_pb2'
  # @@protoc_insertion_point(class_scope:hx2dome.AzEl)
  ))
_sym_db.RegisterMessage(AzEl)

IsComplete = _reflection.GeneratedProtocolMessageType('IsComplete', (_message.Message,), dict(
  DESCRIPTOR = _ISCOMPLETE,
  __module__ = 'hx2dome_pb2'
  # @@protoc_insertion_point(class_scope:hx2dome.IsComplete)
  ))
_sym_db.RegisterMessage(IsComplete)

BasicString = _reflection.GeneratedProtocolMessageType('BasicString', (_message.Message,), dict(
  DESCRIPTOR = _BASICSTRING,
  __module__ = 'hx2dome_pb2'
  # @@protoc_insertion_point(class_scope:hx2dome.BasicString)
  ))
_sym_db.RegisterMessage(BasicString)

Empty = _reflection.GeneratedProtocolMessageType('Empty', (_message.Message,), dict(
  DESCRIPTOR = _EMPTY,
  __module__ = 'hx2dome_pb2'
  # @@protoc_insertion_point(class_scope:hx2dome.Empty)
  ))
_sym_db.RegisterMessage(Empty)



_HX2DOME = _descriptor.ServiceDescriptor(
  name='HX2Dome',
  full_name='hx2dome.HX2Dome',
  file=DESCRIPTOR,
  index=0,
  serialized_options=None,
  serialized_start=217,
  serialized_end=1391,
  methods=[
  _descriptor.MethodDescriptor(
    name='dapiGetAzEl',
    full_name='hx2dome.HX2Dome.dapiGetAzEl',
    index=0,
    containing_service=None,
    input_type=_EMPTY,
    output_type=_AZEL,
    serialized_options=None,
  ),
  _descriptor.MethodDescriptor(
    name='dapiGotoAzEl',
    full_name='hx2dome.HX2Dome.dapiGotoAzEl',
    index=1,
    containing_service=None,
    input_type=_AZEL,
    output_type=_RETURNCODE,
    serialized_options=None,
  ),
  _descriptor.MethodDescriptor(
    name='dapiAbort',
    full_name='hx2dome.HX2Dome.dapiAbort',
    index=2,
    containing_service=None,
    input_type=_EMPTY,
    output_type=_RETURNCODE,
    serialized_options=None,
  ),
  _descriptor.MethodDescriptor(
    name='dapiOpen',
    full_name='hx2dome.HX2Dome.dapiOpen',
    index=3,
    containing_service=None,
    input_type=_EMPTY,
    output_type=_RETURNCODE,
    serialized_options=None,
  ),
  _descriptor.MethodDescriptor(
    name='dapiClose',
    full_name='hx2dome.HX2Dome.dapiClose',
    index=4,
    containing_service=None,
    input_type=_EMPTY,
    output_type=_RETURNCODE,
    serialized_options=None,
  ),
  _descriptor.MethodDescriptor(
    name='dapiPark',
    full_name='hx2dome.HX2Dome.dapiPark',
    index=5,
    containing_service=None,
    input_type=_EMPTY,
    output_type=_RETURNCODE,
    serialized_options=None,
  ),
  _descriptor.MethodDescriptor(
    name='dapiUnpark',
    full_name='hx2dome.HX2Dome.dapiUnpark',
    index=6,
    containing_service=None,
    input_type=_EMPTY,
    output_type=_RETURNCODE,
    serialized_options=None,
  ),
  _descriptor.MethodDescriptor(
    name='dapiFindHome',
    full_name='hx2dome.HX2Dome.dapiFindHome',
    index=7,
    containing_service=None,
    input_type=_EMPTY,
    output_type=_RETURNCODE,
    serialized_options=None,
  ),
  _descriptor.MethodDescriptor(
    name='dapiIsGotoComplete',
    full_name='hx2dome.HX2Dome.dapiIsGotoComplete',
    index=8,
    containing_service=None,
    input_type=_EMPTY,
    output_type=_ISCOMPLETE,
    serialized_options=None,
  ),
  _descriptor.MethodDescriptor(
    name='dapiIsOpenComplete',
    full_name='hx2dome.HX2Dome.dapiIsOpenComplete',
    index=9,
    containing_service=None,
    input_type=_EMPTY,
    output_type=_ISCOMPLETE,
    serialized_options=None,
  ),
  _descriptor.MethodDescriptor(
    name='dapiIsCloseComplete',
    full_name='hx2dome.HX2Dome.dapiIsCloseComplete',
    index=10,
    containing_service=None,
    input_type=_EMPTY,
    output_type=_ISCOMPLETE,
    serialized_options=None,
  ),
  _descriptor.MethodDescriptor(
    name='dapiIsParkComplete',
    full_name='hx2dome.HX2Dome.dapiIsParkComplete',
    index=11,
    containing_service=None,
    input_type=_EMPTY,
    output_type=_ISCOMPLETE,
    serialized_options=None,
  ),
  _descriptor.MethodDescriptor(
    name='dapiIsUnparkComplete',
    full_name='hx2dome.HX2Dome.dapiIsUnparkComplete',
    index=12,
    containing_service=None,
    input_type=_EMPTY,
    output_type=_ISCOMPLETE,
    serialized_options=None,
  ),
  _descriptor.MethodDescriptor(
    name='dapiIsFindHomeComplete',
    full_name='hx2dome.HX2Dome.dapiIsFindHomeComplete',
    index=13,
    containing_service=None,
    input_type=_EMPTY,
    output_type=_ISCOMPLETE,
    serialized_options=None,
  ),
  _descriptor.MethodDescriptor(
    name='dapiSync',
    full_name='hx2dome.HX2Dome.dapiSync',
    index=14,
    containing_service=None,
    input_type=_AZEL,
    output_type=_RETURNCODE,
    serialized_options=None,
  ),
  _descriptor.MethodDescriptor(
    name='deviceInfoNameShort',
    full_name='hx2dome.HX2Dome.deviceInfoNameShort',
    index=15,
    containing_service=None,
    input_type=_EMPTY,
    output_type=_BASICSTRING,
    serialized_options=None,
  ),
  _descriptor.MethodDescriptor(
    name='deviceInfoNameLong',
    full_name='hx2dome.HX2Dome.deviceInfoNameLong',
    index=16,
    containing_service=None,
    input_type=_EMPTY,
    output_type=_BASICSTRING,
    serialized_options=None,
  ),
  _descriptor.MethodDescriptor(
    name='deviceInfoDetailedDescription',
    full_name='hx2dome.HX2Dome.deviceInfoDetailedDescription',
    index=17,
    containing_service=None,
    input_type=_EMPTY,
    output_type=_BASICSTRING,
    serialized_options=None,
  ),
  _descriptor.MethodDescriptor(
    name='deviceInfoFirmwareVersion',
    full_name='hx2dome.HX2Dome.deviceInfoFirmwareVersion',
    index=18,
    containing_service=None,
    input_type=_EMPTY,
    output_type=_BASICSTRING,
    serialized_options=None,
  ),
  _descriptor.MethodDescriptor(
    name='deviceInfoModel',
    full_name='hx2dome.HX2Dome.deviceInfoModel',
    index=19,
    containing_service=None,
    input_type=_EMPTY,
    output_type=_BASICSTRING,
    serialized_options=None,
  ),
])
_sym_db.RegisterServiceDescriptor(_HX2DOME)

DESCRIPTOR.services_by_name['HX2Dome'] = _HX2DOME

# @@protoc_insertion_point(module_scope)
