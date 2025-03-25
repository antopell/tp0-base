package protocol

import (
	"encoding/binary"
	// "fmt"
	"strconv"
)


const IntLength = 4
const CodeLength = 2
const ISODateLength = 10
const BoolLength = 1

// Protocol Entity that encapsulates the creation
// of messages
type Protocol struct {
	messageInCreation []byte
	amountBets				int
	lenWritten				int
	agencyNumber 			string
	maxAmount					int
}

// NewProtocol Initializes a new protocol
func NewProtocol(agencyNumber string, batchMaxAmount int) *Protocol {
	protocol := &Protocol{
		agencyNumber: agencyNumber,
		maxAmount: batchMaxAmount,
	}
	return protocol
}

// TODO: ver donde conviene tener esta informacion
const BetCode = 1
const AgencyCode = 1
const NameCode = 2
const SurnameCode = 3
const DocumentCode = 4
const BirthDateCode = 5
const BetNumberCode = 6

const AckBetCode = 2

// CreateBetMessage Creates a message with the bet info ready to be sent in bytes
func (protocol *Protocol) CreateBetMessage(name string, surname string, document string, birthDateISO string, betNumber string) []byte {
	// Bet message structure:
	// 1|<len>
	// 	<AgencyCode>|<numAgencia>|
	// 	<NameCode>|<len>|<name>|
	// 	<SurnameCode>|<len>|<surname>|
	// 	<DocumentCode>|<document>|
	// 	<BirthDateCode>|<birthDate>|
	// 	<BetNumberCode>|<number>

	// amount codes: 7 (6 campos + codigo inicial)
	// amount int: 6 (agencyNumber + 3 len + document + number)
	lenMessage := CodeLength * 6 + IntLength * 5 + len(name) + len(surname) + ISODateLength
	totalLen := CodeLength + IntLength + lenMessage
	
	protocol.messageInCreation = make([]byte, totalLen)
	protocol.lenWritten = 0


	protocol.addInt(BetCode, lenMessage)

	protocol.addIntFromString(AgencyCode, protocol.agencyNumber)

	protocol.addVariableLenString(NameCode, name)

	protocol.addVariableLenString(SurnameCode, surname)

	protocol.addIntFromString(DocumentCode, document)

	protocol.addString(BirthDateCode, birthDateISO)

	protocol.addIntFromString(BetNumberCode, betNumber)

	return protocol.messageInCreation
}

func (protocol *Protocol) AddToBatch(name string, surname string, document string, birthDateISO string, betNumber string) bool {

	return false
}

func (protocol *Protocol) GetBatchMessage() ([]byte, int) {
	msg := protocol.messageInCreation
	protocol.messageInCreation = make([]byte, 1)
	amount := protocol.amountBets
	protocol.amountBets = 0
	return msg, amount
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

func (protocol *Protocol) addIntFromString(code int, textNumber string) {
	protocol.addCodeToMessage(code)
	protocol.addIntFromStringToMessage(textNumber)
}

func (protocol *Protocol) addVariableLenString(code int, text string){
	protocol.addCodeToMessage(code)
	protocol.addVariableLenStringToMessage(text)
}

func (protocol *Protocol) addInt(code int, number int) {
	protocol.addCodeToMessage(code)
	protocol.addIntToMessage(number)
}

func (protocol *Protocol) addString(code int, text string) {
	protocol.addCodeToMessage(code)
	protocol.addStringToMessage(text)
}

func (protocol *Protocol) DecodeAck(message []byte) bool {
	value := message[CodeLength:] // 1 byte
	trueByte := []byte{1} 
	return value[0] == trueByte[0]
}

func (protocol *Protocol) GetBufferLenAck() int {
	return CodeLength + BoolLength
}
