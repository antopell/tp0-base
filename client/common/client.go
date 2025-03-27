package common

import (
	"bufio"
	// "fmt"
	"net"
	"time"
	"strings"
	"os"
	"os/signal"
	"syscall"

	"github.com/op/go-logging"
	"github.com/7574-sistemas-distribuidos/docker-compose-init/client/protocol"
)

var log = logging.MustGetLogger("log")

// ClientConfig Configuration used by the client
type ClientConfig struct {
	ID            	string
	ServerAddress 	string
	LoopAmount    	int
	LoopPeriod    	time.Duration
	BatchMaxAmount	int
}

// BetData Base information of the bet to send
type BetData struct {
	Name					string
	Surname				string
	Document			string
	BirthDateISO	string
	BettingNumber string
}

// Client Entity that encapsulates how
type Client struct {
	config		ClientConfig
	conn			net.Conn
	protocol 	protocol.Protocol
}

// NewClient Initializes a new client receiving the configuration
// as a parameter
func NewClient(config ClientConfig) *Client {
	client := &Client{
		config: config,
		protocol: *protocol.NewProtocol(config.ID, config.BatchMaxAmount),
	}
	return client
}

// CreateClientSocket Initializes client socket. In case of
// failure, error is printed in stdout/stderr and exit 1
// is returned
func (c *Client) createClientSocket() error {
	conn, err := net.Dial("tcp", c.config.ServerAddress)
	if err != nil {
		log.Criticalf(
			"action: connect | result: fail | client_id: %v | error: %v",
			c.config.ID,
			err,
		)
	}
	c.conn = conn
	return nil
}

// SendMessage sends a message in bytes through the socket
// of the client. Supports short write
func (c *Client) sendMessage(message []byte) {
	lenMessage := len(message)
	bytesWritten := 0

	// Continues writing until it's all sent
	for bytesWritten < lenMessage {
		written, err := c.conn.Write(message[bytesWritten:])
		if err != nil {
			log.Criticalf(
				"action: send message | result: fail | client_id: %v | error: %v",
				c.config.ID,
				err,
			)
		}
		bytesWritten += written
	}
}

// StartClientLoop Send messages to the client until some time threshold is met
func (c *Client) StartClientLoop() {
	signalChannel := make(chan os.Signal, 1)
	signal.Notify(signalChannel, syscall.SIGTERM, syscall.SIGINT)

	file, err := os.Open("./agencyFile.csv")
	if err != nil {
		log.Criticalf(
			"action: open file | result: fail | error: %v",
			err,
		)
	}
	defer file.Close()
	scanner := bufio.NewScanner(file)

	c.createClientSocket()
	defer c.conn.Close()

	for scanner.Scan() {
		line := scanner.Text()

		betData, failed := c.lineToBetData(line)
		if failed {
			continue
		}

		readyToSend := c.protocol.AddToBatch(betData.Name, betData.Surname, betData.Document, betData.BirthDateISO, betData.BettingNumber)
		if readyToSend {
			c.sendBatch(false)
		}
		

		select {
		case sig := <-signalChannel:
			log.Infof("action: exit | result: success | client_id: %v | signal: %v", c.config.ID, sig)
			return
		default:
		}

	}
	c.sendBatch(true)
	// log.Infof("action: loop_finished | result: success | client_id: %v", c.config.ID)
}

func (c *Client) getAck() bool {
	lenAck := c.protocol.GetBufferLenAck()

	message := c.full_read(lenAck)
	result := c.protocol.DecodeAck(message)
	return result
}

func (c *Client) full_read(amountToRead int) []byte {
	amountRead := 0
	fullmessage := make([]byte, amountToRead)
	for amountRead < amountToRead {
		read, err := c.conn.Read(fullmessage)
		amountRead += read

		if err != nil {
			log.Errorf("action: receive_message | result: fail | client_id: %v | error: %v",
				c.config.ID,
				err,
			)
			return nil
		}
	}
	return fullmessage
}


func (c *Client) lineToBetData(line string) (BetData, bool) {
	fields := strings.Split(line, ",")
	if len(fields) < 5 {
		log.Errorf("action: parse line | result: fail | Not enough fields")
		return BetData{}, true
	}
	betData := BetData{
		Name:						fields[0],
		Surname:				fields[1],
		Document:				fields[2],
		BirthDateISO:		fields[3],
		BettingNumber:	fields[4],
	}

	return betData, false

}

func (c *Client) sendBatch(lastSend bool) {
	message := c.protocol.GetBatchMessage(lastSend)
	if len(message) == 0 {
		return
	}
	c.sendMessage(message)

	msg := c.getAck()
	if msg {
		log.Infof("action: apuesta_enviada | result: success")
	} else {
		log.Infof("action: apuesta_enviada | result: fail")
	}
}
