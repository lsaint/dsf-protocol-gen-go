# -*- coding: utf-8 -*-

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


def writeconv(field):
    t = field.attrib.get("type").lower()
    n = field.attrib.get("name").title()
    if t in ("int8","uint8","int16","uint16","int32", "uint32","int64", "uint64"):
        return "\tWriteCommon(buffer, L.{0})\n".format(n)
    if t == "string":
        return "\tWriteString(buffer, L.{0})\n".format(n)
    if t in ("vector", "list", "set"):
        return "\tWriteList(buffer, L.{0})\n".format(n)
    if t == "map":
        return "\tWriteMap(buffer, L.{0})\n".format(n)
    if t == "binary":
        return "\tWriteBinary(buffer, L.{0})\n".format(n)
    print "write unsupport field type", t
    exit(-1)


def readconv(field):
    t = field.attrib.get("type").lower()
    n = field.attrib.get("name").title()
    if t in ("int8","uint8","int16","uint16","int32", "uint32","int64", "uint64"):
        return "\tReadCommon(buffer, &L.{0})\n".format(n)
    if t == "string":
        return "\tL.{0}, _ = ReadString(buffer)\n".format(n)
    if t in ("vector", "list", "set"):
        return "\tL.{0}, _ = ReadList(buffer)\n".format(n)
    if t == "map":
        return "\tL.{0}, _ = ReadMap(buffer)\n".format(n)
    if t == "binary":
        return "\tL.{0}, _ = ReadBinary(buffer)\n".format(n)
    print "read unsupport field type", t
    exit(-1)



def genObject(entity):
    struct_name = entity.attrib.get("name").title()
    # define
    ret = "type {0} struct {1}\n".format(struct_name, "{")
    for field in entity:
        print "--", field.tag, field.attrib
        ret = "{0}{1}".format(ret, genObjectField(field))
    ret = ret + "}\n\n"

    # func Marshal
    ret = ret + "func (L *{0}) Marshal() ([]byte, error) {1}\n{2}".format(
            struct_name, "{", "\tbuffer := new(bytes.Buffer)\n")
    for field in entity:
        ret = "{0}{1}".format(ret, writeconv(field))
    ret = ret + "\treturn buffer.Bytes(), nil\n}\n\n"

    # func Unmarshal
    ret = ret + "func (L *{0}) Unmarshal(b []byte) error {1}\n{2}".format(
            struct_name, "{", "\tbuffer := bytes.NewBuffer(b)\n")
    for field in entity:
        ret = "{0}{1}".format(ret, readconv(field))
    ret = ret + "\treturn nil\n}\n\n"

    return ret


def genObjectField(field):
    return "\t{0}\t{1}\t\\\\{2}\n".format(field.attrib.get("name").title(),
                             typeconv(field),
                             utf8(field.attrib.get("desc")) or "")


###

def genConstNum(entity):
    pass


def genConstStr(entity):
    pass


tree = parser("l.dsfp", "gbk")
root = tree.getroot()
print root.tag, root.attrib

for protocol in root:
    if protocol.tag == "protocol":
        for entity in protocol:
            print entity.tag, entity.attrib
            t = entity.attrib.get("type").lower()
            if t == "object":
                print genObject(entity)
            elif t == "numeric_constant":
                genConstNum(entity)
            elif t == "string_constant":
                genConstStr(entity)

