package protocol

import (
	"encoding/binary"
	// "fmt"
	"strconv"
	"github.com/op/go-logging"
)

var log = logging.MustGetLogger("log")

const IntLength = 4
const CodeLength = 2
const ISODateLength = 10
const BoolLength = 1

// Protocol Entity that encapsulates the creation
// of messages
type Protocol struct {
	messageInCreation []byte
	betInCreation 		[]byte
	messageToSend		  []byte
	amountBets				int	
	lenWritten				int // to help with the writing of each bet
	agencyNumber 			string
	maxAmount					int
}

const maxMessageSize = 8192 // 8kB

// NewProtocol Initializes a new protocol
func NewProtocol(agencyNumber string, batchMaxAmount int) *Protocol {
	protocol := &Protocol{
		agencyNumber: agencyNumber,
		maxAmount: batchMaxAmount,
	}
	return protocol
}

// TODO: ver donde conviene tener esta informacion
const BatchBetCode = 2
const	AgencyBatchCode = 2

const BetCode = 1
const	AgencyCode = 1
const NameCode = 2
const SurnameCode = 3
const DocumentCode = 4
const BirthDateCode = 5
const BetNumberCode = 6

const AckBetCode = 3

// createBetMessage Creates a message with the bet info ready to be sent in bytes
func (protocol *Protocol) createBetMessage(name string, surname string, document string, birthDateISO string, betNumber string) []byte {
	// Bet message structure:
	// 1|<len>
	// 	<NameCode>|<len>|<name>|
	// 	<SurnameCode>|<len>|<surname>|
	// 	<DocumentCode>|<document>|
	// 	<BirthDateCode>|<birthDate>|
	// 	<BetNumberCode>|<number>

	// amount codes: 6 (5 campos + codigo inicial)
	// amount int: 4 (2 len + document + number)
	lenMessage := CodeLength * 5 + IntLength * 4 + len(name) + len(surname) + ISODateLength
	totalLen := CodeLength + IntLength + lenMessage
	
	protocol.betInCreation = make([]byte, totalLen)
	protocol.lenWritten = 0

	protocol.addInt(BetCode, lenMessage)

	protocol.addVariableLenString(NameCode, name)

	protocol.addVariableLenString(SurnameCode, surname)

	protocol.addIntFromString(DocumentCode, document)

	protocol.addString(BirthDateCode, birthDateISO)

	protocol.addIntFromString(BetNumberCode, betNumber)

	return protocol.betInCreation
}

func (protocol *Protocol) AddToBatch(name string, surname string, document string, birthDateISO string, betNumber string) bool {
	isReady := false
	if protocol.amountBets == 0 {
		protocol.messageInCreation = []byte{}
	}
	betMessage := protocol.createBetMessage(name, surname, document, birthDateISO, betNumber)
	newLen := len(betMessage) + len(protocol.messageInCreation) + CodeLength + IntLength
	if newLen > maxMessageSize {
		// message would be too big
		protocol.resetBatchMessage()
		isReady = true
	}

	protocol.amountBets += 1
	protocol.messageInCreation = append(protocol.messageInCreation, betMessage...)
	if protocol.amountBets == protocol.maxAmount {
		protocol.resetBatchMessage()
		isReady = true
	}

	return isReady
}

func (protocol *Protocol) resetBatchMessage() {
	protocol.amountBets = 0
	protocol.messageToSend = protocol.messageInCreation
	protocol.messageInCreation = []byte{}
}

func (protocol *Protocol) GetBatchMessage(forceSend bool) []byte {
	if forceSend {
		protocol.resetBatchMessage()
	}
	lenBatch := len(protocol.messageToSend)
	if lenBatch == 0 {
		return []byte{}
	}
	lenBatchMsg := CodeLength + IntLength + lenBatch
	totalLen := CodeLength + IntLength +lenBatchMsg
	message := make([]byte, totalLen)

	binary.BigEndian.PutUint16(message, uint16(BatchBetCode))
	lenWritten := CodeLength;

	binary.BigEndian.PutUint32(message[lenWritten:], uint32(lenBatchMsg))
	lenWritten += IntLength

	binary.BigEndian.PutUint16(message[lenWritten:], uint16(AgencyBatchCode))
	lenWritten += CodeLength;

	agencyNumber, _ := strconv.Atoi(protocol.agencyNumber)
	binary.BigEndian.PutUint32(message[lenWritten:], uint32(agencyNumber))
	lenWritten += IntLength

	copy(message[lenWritten:], protocol.messageToSend)

	return message
}

func (protocol *Protocol) addCodeToMessage(code int) {
	messageCode := uint16(code)
	binary.BigEndian.PutUint16(protocol.betInCreation[protocol.lenWritten:], messageCode)
	protocol.lenWritten += CodeLength
}

func (protocol *Protocol) addIntToMessage(number int) {
	messageNumber := uint32(number)
	binary.BigEndian.PutUint32(protocol.betInCreation[protocol.lenWritten:], messageNumber)
	protocol.lenWritten += IntLength
}

func (protocol *Protocol) addStringToMessage(text string) {
	stringBytes := []byte(text) 
	copy(protocol.betInCreation[protocol.lenWritten:], stringBytes)
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
