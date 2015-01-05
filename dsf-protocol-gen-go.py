#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import xml.etree.cElementTree as ET
import codecs


def parser(f, encoding):
    f = codecs.open(f, "r", encoding)
    p = ET.XMLParser(encoding="utf-8")
    while 1:
        s = f.read(65536)
        if not s:
            break
        p.feed(s.encode("utf-8"))
    return ET.ElementTree(p.close())


def utf8(s):
    if s:
        return s.encode("utf-8")
    return

### 

g_header = '''// L'Code generated by dsf-protocol-gen-go.
// L'source: {0}
// L'DO NOT EDIT!

package {1}

import (
\t"bytes"
\t. "github.com/lsaint/yyprotogo"
)

'''

g_const = '''const (
{0})

'''

g_uri = '''var URI = map[string]uint32 {{
{0}}}

var URI_R  map[uint32]string

func init() {{
    for name, uri := range URI {{
        URI_R[uri] = name
    }}
}}

'''


def typeconv(field):
    t = field.attrib.get("type").lower()
    if t in ("int8","uint8","int16","uint16","int32", "uint32","int64", "uint64", "string"):
        return t
    if t in ("vector", "list", "set"):
        v = field.attrib.get("value_type")
        return "[]{0}".format(v)
    if t == "map":
        k = field.attrib.get("key_type")
        v = field.attrib.get("value_type")
        return "map[{0}]{1}".format(k, v)
    if t == "binary":
        return "[]byte"
    print "unsupport field type", t
    exit(-1)


def iscommon(t):
    return t in ("int8","uint8","int16","uint16","int32", "uint32","int64", "uint64")


def writeconv(field):
    t = field.attrib.get("type").lower()
    n = field.attrib.get("name").title()
    if iscommon(t):
        return "\tWriteCommon(buffer, L.{0})\n".format(n)
    if t == "string":
        return "\tWriteString(buffer, L.{0})\n".format(n)
    if t in ("vector", "list", "set"):
        vt = field.attrib.get("value_type").lower()
        return wrap_WriteList(vt, n)
    if t == "map":
        vk = field.attrib.get("key_type").lower()
        vt = field.attrib.get("value_type").lower()
        return wrap_WriteMap(vk, vt, n)
    if t == "binary":
        return "\tWriteBinary(buffer, L.{0})\n".format(n)
    print "write unsupport field type", t
    exit(-1)


writelist = """\tWriteCommon(buffer, uint32(len(L.{0})))
\tfor _, item := range L.{0} {{
\t    Write{1}(buffer, item)
\t}}
"""
def wrap_WriteList(vt, n):
    return writelist.format(n, get_subfix(vt))


def get_subfix(i):
    if iscommon(i):
        return "Common"
    return "String"


writemap = """\tWriteCommon(buffer, uint32(len(L.{0})))
\tfor k, v := range L.{0} {{
\t    Write{1}(buffer, k)
\t    Write{2}(buffer, v)
\t}}
"""
def wrap_WriteMap(vk, vt, n):
    return writemap.format(n, get_subfix(vk), get_subfix(vt))


def readconv(field):
    t = field.attrib.get("type").lower()
    n = field.attrib.get("name").title()
    if t in ("int8","uint8","int16","uint16","int32", "uint32","int64", "uint64"):
        return "\tReadCommon(buffer, &L.{0})\n".format(n)
    if t == "string":
        return "\tL.{0}, _ = ReadString(buffer)\n".format(n)
    if t in ("vector", "list", "set"):
        vt = field.attrib.get("value_type").lower()
        return wrap_ReadList(n, vt)
    if t == "map":
        vk = field.attrib.get("key_type").lower()
        vt = field.attrib.get("value_type").lower()
        return wrap_ReadMap(n, vk, vt)
    if t == "binary":
        return "\tL.{0}, _ = ReadBinary(buffer)\n".format(n)
    print "read unsupport field type", t
    exit(-1)


readlist = """\tvar len_{0} uint32
\tReadCommon(buffer, &len_{0})
\tL.{0} = make([]{1}, int(len_{0}))
\tfor i := 0; i < int(len_{0}); i++ {{
\t\t{2}
\t\tL.{0}[i] = {0}_v
\t}}
"""
def wrap_ReadList(n, vt):
    return readlist.format(n, vt, get_ReadInnerLoop(n+"_v", vt))


def get_ReadInnerLoop(var_name, vt):
    if iscommon(vt):
        return "var {0} {1}\n\t\tReadCommon(buffer, &{0})".format(var_name, vt)
    return "{0}, _ := ReadString(buffer)".format(var_name)


readmap = """\tvar len_{0} uint32
\tReadCommon(buffer, &len_{0})
\tL.{0} = make(map[{1}]{2})
\tfor i := 0; i < int(len_{0}); i++ {{
\t\t{3}
\t\t{4}
\t\tL.{0}[{0}_k] = {0}_v
\t}}
"""
def wrap_ReadMap(n, vk, vt):
    return readmap.format(n, vk, vt, get_ReadInnerLoop(n+"_k", vk), get_ReadInnerLoop(n+"_v", vt))


def genObject(entity):
    struct_name = entity.attrib.get("name")
    struct_desc = utf8(entity.attrib.get("desc")) or ""

    define_head = "//{0}\ntype {1} struct {{\n".format(struct_desc, struct_name)
    define_body = ""
    define_tail = "}\n\n"

    marshal_head = "func (L *{0}) Marshal() ([]byte, error) {{\n{1}".format(
                        struct_name, "\tbuffer := new(bytes.Buffer)\n")
    marshal_body = ""
    marshal_tail = "\treturn buffer.Bytes(), nil\n}\n\n"

    unmarshal_head = "func (L *{0}) Unmarshal(b []byte) error {{\n{1}".format(
                        struct_name, "\tbuffer := bytes.NewBuffer(b)\n")
    unmarshal_body = ""
    unmarshal_tail = "\treturn nil\n}\n\n"

    for field in entity:
        define_body     = "{0}{1}".format(define_body, genObjectField(field))
        marshal_body    = "{0}{1}".format(marshal_body, writeconv(field))
        unmarshal_body  = "{0}{1}".format(unmarshal_body, readconv(field))

    define_complete     = "{0}{1}{2}".format(define_head, define_body, define_tail)
    marshal_complete    = "{0}{1}{2}".format(marshal_head, marshal_body, marshal_tail)
    unmarshal_complete  = "{0}{1}{2}".format(unmarshal_head, unmarshal_body, unmarshal_tail)

    return "{0}{1}{2}".format(define_complete, marshal_complete, unmarshal_complete)


def genObjectField(field):
    return "\t{0}\t{1}\t//{2}\n".format(field.attrib.get("name").title(),
                             typeconv(field),
                             utf8(field.attrib.get("desc")) or "")


###

def genUri(entity):
    service_id = entity.attrib.get("service_id")
    if service_id is None:
        return ""
    command_id = entity.attrib.get("command_id")
    name = entity.attrib.get("name")
    compat = False
    if entity.attrib.get("compat") == "true":
        compat = True
    if compat:
        return '\t"{0}"\t: (uint32({1}) << 8) | uint32({2}),\n'.format(name, service_id, command_id)
    else:
        return '\t"{0}"\t: (uint32({1}) << 16) | uint32({2}),\n'.format(name, service_id, command_id)


def genConstNum(entity):
    k = entity.attrib.get("name")
    v = entity.attrib.get("value")
    if k and v:
        return "\t{0}\t= {1}\n".format(k, v)
    return ""


def genConstStr(entity):
    k = entity.attrib.get("name")
    v = entity.attrib.get("value")
    if k and v:
        return '\t{0}\t= "{1}"\n'.format(k, v)
    return ""


###

if len(sys.argv) < 2:
    print "missing dsfp file"
    print "eg. >>dsf-protocol-gen-go l.dsfp gbk"
    exit(0)

dsfp = sys.argv[1]
encoding = sys.argv[2] if len(sys.argv) > 2 else "gbk"

tree = parser(dsfp, encoding)
root = tree.getroot()

for protocol in root:
    if protocol.tag == "protocol":
        package_name =  protocol.attrib.get("ns")
        if package_name is None:
            print 'missing <protocol ns="go-package-name">'
            exit(-1)
        g_header = g_header.format(dsfp, package_name)

        consts = ""
        entities = ""
        uris = ""
        for entity in protocol:
            #print entity.tag, entity.attrib
            t = entity.attrib.get("type").lower()
            if t == "object":
                entities = entities + genObject(entity)
                uris = uris + genUri(entity)
            elif t == "numeric_constant":
                consts = consts + genConstNum(entity)
            elif t == "string_constant":
                consts = consts + genConstStr(entity)

        if consts:
            consts = g_const.format(consts)
        if uris:
            uris = g_uri.format(uris)
        print "{0}{1}{2}{3}".format(g_header, consts, uris, entities)

