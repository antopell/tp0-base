package common

import (
	// "bufio"
	// "fmt"
	"net"
	"time"
	"os"
	"os/signal"
	"syscall"

	"github.com/op/go-logging"
	"github.com/7574-sistemas-distribuidos/docker-compose-init/client/protocol"
)

var log = logging.MustGetLogger("log")

// ClientConfig Configuration used by the client
type ClientConfig struct {
	ID            string
	ServerAddress string
	LoopAmount    int
	LoopPeriod    time.Duration
}

// ClientData General information of the client
type ClientData struct {
	Name					string
	Surname				string
	Dni						string
	BirthDateISO	string
	BettingNumber string
}

// Client Entity that encapsulates how
type Client struct {
	config		ClientConfig
	conn			net.Conn
	data 			ClientData
	protocol 	protocol.Protocol
}

// NewClient Initializes a new client receiving the configuration
// as a parameter
func NewClient(config ClientConfig, data ClientData) *Client {
	client := &Client{
		config: config,
		data: data,
		protocol: *protocol.NewProtocol(),
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

	// There is an autoincremental msgID to identify every message sent
	// Messages if the message amount threshold has not been surpassed
	// for msgID := 1; msgID <= c.config.LoopAmount; msgID++ {

	c.createClientSocket()

	data := c.data
	message := c.protocol.CreateBetMessage(c.config.ID, data.Name, data.Surname, data.Dni, data.BirthDateISO, data.BettingNumber)
	c.sendMessage(message)

	msg := c.getAck()
	if msg {
		log.Infof("action: apuesta_enviada | result: success | dni: %v | numero: %v",
			data.Dni,
			data.BettingNumber,
		)
	} else {
		log.Infof("action: apuesta_enviada | result: fail | dni: %v | numero: %v",
			data.Dni,
			data.BettingNumber,
		)
	}
	
	
	c.conn.Close()

	select {
	case sig := <-signalChannel:
		// c.conn should be closed by now 
		c.conn.Close() // just in case
		log.Infof("action: exit | result: success | client_id: %v | signal: %v", c.config.ID, sig)
		return
	default:
	}

	// }
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
