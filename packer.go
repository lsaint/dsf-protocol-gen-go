package yyprotogo

import (
	"bytes"
	"encoding/binary"
)

type YYMarshalable interface {
	Marshal() ([]byte, error)
	Unmarshal([]byte) error
}

func WriteMarshalable(buffer *bytes.Buffer, ma YYMarshalable) {
	if b, err := ma.Marshal(); err == nil {
		binary.Write(buffer, binary.LittleEndian, b)
	}
}

func WriteCommon(buffer *bytes.Buffer, i interface{}) {
	binary.Write(buffer, binary.LittleEndian, i)
}

func WriteString(buffer *bytes.Buffer, s string) {
	binary.Write(buffer, binary.LittleEndian, uint16(len(s))+1)
	binary.Write(buffer, binary.LittleEndian, []byte(s+"\x00"))
}

func WriteBinary(buffer *bytes.Buffer, b []byte) {
	binary.Write(buffer, binary.LittleEndian, uint32(len(b)))
	binary.Write(buffer, binary.LittleEndian, b)
}

//func WriteFloat(buffer *bytes.Buffer, f float32) {
//	WriteString(buffer, strconv.FormatFloat(float64(f), 'f', 5, 32))
//}
//
//func WriteDouble(buffer *bytes.Buffer, f float64) {
//	WriteString(buffer, strconv.FormatFloat(f, 'f', 5, 64))
//}

//func WriteList(buffer *bytes.Buffer, lt []string) {
//	binary.Write(buffer, binary.LittleEndian, uint32(len(lt)))
//	for _, item := range lt {
//		WriteString(buffer, item)
//	}
//}

//func WriteMap(buffer *bytes.Buffer, m map[int32]string) {
//	binary.Write(buffer, binary.LittleEndian, uint32(len(m)))
//	for k, v := range m {
//		WriteCommon(buffer, k)
//		WriteString(buffer, v)
//	}
//}

//

func ReadCommon(buffer *bytes.Buffer, i interface{}) {
	binary.Read(buffer, binary.LittleEndian, i)
}

func ReadString(buffer *bytes.Buffer) (string, error) {
	var l uint16
	binary.Read(buffer, binary.LittleEndian, &l)
	b := buffer.Next(int(l))
	return string(b[:l-1]), nil
}

func ReadBinary(buffer *bytes.Buffer) (b []byte, err error) {
	var l uint32
	binary.Read(buffer, binary.LittleEndian, &l)
	b = buffer.Next(int(l))
	return
}

//func ReadList(buffer *bytes.Buffer) (lt []string, err error) {
//	var l uint32
//	binary.Read(buffer, binary.LittleEndian, &l)
//	lt = make([]string, int(l))
//	for i := 0; i < int(l); i++ {
//		lt[i], _ = ReadString(buffer)
//	}
//	return
//}
//
//func ReadMap(buffer *bytes.Buffer) (m map[int32]string, err error) {
//	var l uint32
//	binary.Read(buffer, binary.LittleEndian, &l)
//	m = make(map[int32]string)
//	var k int32
//	var v string
//	for i := 0; i < int(l); i++ {
//		ReadCommon(buffer, &k)
//		v, _ = ReadString(buffer)
//		m[k] = v
//	}
//	return
//}
