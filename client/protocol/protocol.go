package protocol

import (
	"encoding/binary"
	"fmt"
	// "strconv"
)


const IntLength = 4
const CodeLegth = 2
const ISODateLegth = 10

// Protocol Entity that encapsulates the creation
// of messages
type Protocol struct {
}

// NewProtocol Initializes a new protocol
func NewProtocol() *Protocol {
	protocol := &Protocol{}
	return protocol
}

// TODO: ver donde conviene tener esta informacion
const BetCode = 1
const NameCode = 1
const SurnameCode = 2
const DNICode = 3
const BirthDateCode = 4
const BetNumberCode = 5

// CreateBetMessage Creates a message with the bet info ready to be sent in bytes
func (protocol *Protocol) CreateBetMessage(name string, surname string, dni string, birthDateISO string, betNumer string) []byte {
	// Bet message structure:
	// 1|1|<largo>|<nombre>|2|<largo>|<apellido>|3|<dni>|4|<fecha>|5|<numero>

	// cantidad codigos: 6 (5 campos + codigo inicial)
	// cantidad int: 4 (2 largos + dni + numero)
	nameLen := len(name)
	surnameLen := len(surname)
	lenMessage := CodeLegth * 6 + IntLength * 4 + nameLen + surnameLen + ISODateLegth

	message := make([]byte, lenMessage)
	messageCode := uint16(BetCode)
	binary.BigEndian.PutUint16(message[0:], messageCode)

	nameCode := uint16(NameCode)
	binary.BigEndian.PutUint16(message[2:], nameCode)

	fmt.Printf("% x\n", message)

	return message
}
