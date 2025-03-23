package protocol

import (
	"encoding/binary"
	"fmt"
	"strconv"
)


const IntLength = 4
const CodeLength = 2
const ISODateLength = 10

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
const AgencyCode = 1
const NameCode = 2
const SurnameCode = 3
const DNICode = 4
const BirthDateCode = 5
const BetNumberCode = 6

// CreateBetMessage Creates a message with the bet info ready to be sent in bytes
func (protocol *Protocol) CreateBetMessage(agencyNumber string, name string, surname string, dni string, birthDateISO string, betNumber string) []byte {
	// Bet message structure:
	// 1|<len>
	// 	<AgencyCode>|<numAgencia>|
	// 	<NameCode>|<len>|<name>|
	// 	<SurnameCode>|<len>|<surname>|
	// 	<DNICode>|<dni>|
	// 	<BirthDateCode>|<birthDate>|
	// 	<BetNumberCode>|<number>

	// amount codes: 7 (6 campos + codigo inicial)
	// amount int: 6 (agencyNumber + 3 len + dni + number)
	lenMessage := CodeLength * 6 + IntLength * 5 + len(name) + len(surname) + ISODateLength
	totalLen := CodeLength + IntLength + lenMessage
	
	protocol.messageInCreation = make([]byte, totalLen)
	protocol.lenWritten = 0

	protocol.addCodeToMessage(BetCode)
	protocol.addIntToMessage(lenMessage)

	protocol.addCodeToMessage(AgencyCode)
	protocol.addIntFromStringToMessage(agencyNumber)

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
	protocol.lenWritten += CodeLength
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
