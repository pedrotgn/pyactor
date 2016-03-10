
import socket
from socket import AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from threading import Thread
import types, struct, cPickle, sys

class Server:
    def __init__(self, host, port, listener):
        listenSocket = socket.socket(AF_INET, SOCK_STREAM)
        listenSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        listenSocket.bind((host, port))
        listenSocket.listen(10)
        #print "SERVER: Listening"
        self.sockets = {}
        self.endpoints={}
        self.socket = listenSocket
        self.listener = listener
        self.thread = Thread(target=self.AcceptConnections, args=[listenSocket])
        self.thread.start()


    def AcceptConnections(self, listenSocket):
        while True:
            self.AcceptEndpointConnections(listenSocket)


    def AcceptEndpointConnections(self, listenSocket):
        clientSocket, clientAddress = listenSocket.accept()
        #print "SERVER: Accepted connection from", clientAddress
        #print "SERVER: Client socket", id(clientSocket._sock)
        EndPoint(self, clientSocket)

    def send(self, msg):
        addr = msg[0]
        data = cPickle.dumps(msg[1])
        conn = None

        if self.endpoints.has_key(addr):
            end_point = self.endpoints[addr]
            conn = end_point.socket
        else:
            conn = socket.socket(AF_INET, SOCK_STREAM)
            (ip, port) = addr
            conn.connect((ip, int(port)))

            self.endpoints[addr] = EndPoint(self, conn)

        conn.send(struct.pack("!I", len(data)))
        conn.send(data)

    def close(self):
        #print "SERVER: Shutting down the server"
        try:
            self.socket.shutdown(1)
        except:
            None
        self.socket.close()
        for endpoint in self.endpoints.values():
            endpoint.Release()
        self.thread._Thread__stop()



class EndPoint:
    packetSizeFmt = "!I"
    packetSizeLength = struct.calcsize(packetSizeFmt)

    def __init__(self, server, epSocket):
        self.socket = epSocket

        self.server = server
        self.init = False

        self.thread = Thread(target=self._ManageSocket)
        self.thread.start()

    def Release(self):
        self.socket.close()
        self.thread._Thread__stop()

    def _ManageSocket(self):
        try:
            self._ReceivePackets()
        except socket.error, e:
            self.Release()

    def _ReceivePackets(self):
        rawPacket = self._ReadIncomingPacket()
        while rawPacket:
            self._DispatchIncomingPacket(rawPacket)
            rawPacket = self._ReadIncomingPacket()

    def _ReadIncomingPacket(self):
        sizeData = self._ReadIncomingData(self.packetSizeLength)
        if sizeData:
            dataLength = struct.unpack(self.packetSizeFmt, sizeData)[0]
            return self._ReadIncomingData(dataLength)

    def _ReadIncomingData(self, dataLength):
        readBuffer = ""
        while len(readBuffer) != dataLength:
            data = self.socket.recv(dataLength - len(readBuffer))
            if not data:
                self.Release()
            readBuffer += data

        return readBuffer

    def _DispatchIncomingPacket(self, rawPacket):
        msg = cPickle.loads(rawPacket)
        if not self.init:
            self.server.endpoints[msg[0]]=self
            self.init= True
        self.server.listener.on_message(msg[1])

    def _SendPacket(self, packetType, callID, payload):
        data = cPickle.dumps((packetType, callID, payload))
        self.socket.send(struct.pack("!I", len(data)))
        self.socket.send(data)

    def send(self,data):
        print 'aoooo'
        self.socket.send(struct.pack("!I", len(data)))
        # Packet data.
        print data
        self.socket.send(data)
