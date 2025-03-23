package protocol

import (
	"encoding/binary"
	"fmt"
	"strconv"
)


const IntLength = 4
const CodeLegth = 2
const ISODateLegth = 10

// Protocol Entity that encapsulates the creation
// of messages
type Protocol struct {
	messageInCreation []byte
	lenWritten				int
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
func (protocol *Protocol) CreateBetMessage(name string, surname string, dni string, birthDateISO string, betNumber string) []byte {
	// Bet message structure:
	// 1|1|<largo>|<nombre>|2|<largo>|<apellido>|3|<dni>|4|<fecha>|5|<numero>

	// cantidad codigos: 6 (5 campos + codigo inicial)
	// cantidad int: 4 (2 largos + dni + numero)
	nameLen := len(name)
	surnameLen := len(surname)
	lenMessage := CodeLegth * 6 + IntLength * 4 + nameLen + surnameLen + ISODateLegth
	
	protocol.messageInCreation = make([]byte, lenMessage)
	protocol.lenWritten = 0

	protocol.addCodeToMessage(BetCode)

	protocol.addCodeToMessage(NameCode)
	protocol.addVariableLenStringToMessage(name)

	protocol.addCodeToMessage(SurnameCode)
	protocol.addVariableLenStringToMessage(surname)

	protocol.addCodeToMessage(DNICode)
	protocol.addIntFromStringToMessage(dni)

	protocol.addCodeToMessage(BirthDateCode)
	protocol.addStringToMessage(birthDateISO)

	protocol.addCodeToMessage(BetNumberCode)
	protocol.addIntFromStringToMessage(betNumber)


	fmt.Printf("%x\n", protocol.messageInCreation)

	return protocol.messageInCreation
}

func (protocol *Protocol) addCodeToMessage(code int) {
	messageCode := uint16(code)
	binary.BigEndian.PutUint16(protocol.messageInCreation[protocol.lenWritten:], messageCode)
	protocol.lenWritten += CodeLegth
}

func (protocol *Protocol) addIntToMessage(number int) {
	messageNumber := uint32(number)
	binary.BigEndian.PutUint32(protocol.messageInCreation[protocol.lenWritten:], messageNumber)
	protocol.lenWritten += IntLength
}

func (protocol *Protocol) addStringToMessage(text string) {
	stringBytes := []byte(text) 
	copy(protocol.messageInCreation[protocol.lenWritten:], stringBytes)
	protocol.lenWritten += len(stringBytes)
}

func (protocol *Protocol) addVariableLenStringToMessage(text string) {
	protocol.addIntToMessage(len(text))
	protocol.addStringToMessage(text)
}

func (protocol *Protocol) addIntFromStringToMessage(textNumber string) {
	intValue, _ := strconv.Atoi(textNumber)
	protocol.addIntToMessage(intValue)
}
