package yyprotogo

import (
	"bytes"
	"testing"
)

type YP1 struct {
	Uid  uint32
	Name string
	Pets []string
	Mm   map[int32]string
	Bin  []byte
}

func (L *YP1) Marshal() ([]byte, error) {
	buffer := new(bytes.Buffer)
	WriteCommon(buffer, L.Uid)
	WriteString(buffer, L.Name)
	WriteList(buffer, L.Pets)
	WriteMap(buffer, L.Mm)
	WriteBinary(buffer, L.Bin)
	return buffer.Bytes(), nil
}

func (L *YP1) Unmarshal(b []byte) error {
	buffer := bytes.NewBuffer(b)
	ReadCommon(buffer, &L.Uid)
	L.Name, _ = ReadString(buffer)
	L.Pets, _ = ReadList(buffer)
	L.Mm, _ = ReadMap(buffer)
	L.Bin, _ = ReadBinary(buffer)
	return nil
}

func TestPack(t *testing.T) {
	yp1 := &YP1{
		Uid:  uint32(10000),
		Name: "lSaint",
		Pets: []string{"1", "2"},
		Mm:   map[int32]string{1: "11", 2: "22"},
		Bin:  []byte{'\x97', '\x98'}}

	b, err := yp1.Marshal()
	if err != nil {
		t.Fatal("Marshal err", err)
	}

	var yp11 YP1
	if err := yp11.Unmarshal(b); err != nil {
		t.Fatal("Unmarshal err", err)
	}

	if yp11.Uid != yp1.Uid {
		t.Fatal("common type unmatch")
	}

	if yp11.Name != yp1.Name {
		t.Fatal("string unmatch")
	}

	for i := 0; i < len(yp1.Pets); i++ {
		if yp1.Pets[i] != yp11.Pets[i] {
			t.Fatal("list unmatch")
		}
	}

	if yp1.Mm[1] != yp11.Mm[1] || yp1.Mm[2] != yp11.Mm[2] {
		t.Fatal("map unmatch")
	}

	for i := 0; i < len(yp1.Bin); i++ {
		if yp1.Bin[i] != yp11.Bin[i] {
			t.Fatal("binary unmatch")
		}
	}

	if yp1.Mm[1] != yp11.Mm[1] || yp1.Mm[2] != yp11.Mm[2] {
		t.Fatal("map unmatch")
	}
}
