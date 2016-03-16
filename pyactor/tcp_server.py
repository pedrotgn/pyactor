
import socket
from socket import AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from threading import Thread
import types, struct, cPickle, sys
from tcp import TCPDispatcher

class Server:
    def __init__(self, addr):
        listenSocket = socket.socket(AF_INET, SOCK_STREAM)
        listenSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        host,port = addr
        listenSocket.bind((host, int(port)))
        listenSocket.listen(10)
        #print "SERVER: Listening"
        self.addr = addr
        self.sockets = {}
        self.endpoints={}
        self.socket = listenSocket
        #self.addr = host,port
        #self.listener = listener
        self.thread = Thread(target=self.accept_connections, args=[listenSocket])
        self.thread.start()


    def accept_connections(self, listenSocket):
        while True:
            self.accept_endpoint_connections(listenSocket)

    def accept_endpoint_connections(self, listenSocket):
        clientSocket, clientAddress = listenSocket.accept()
        EndPoint(self, clientSocket,self.addr)

    def get_dispatcher(self,addr):
        ep = self.get_endpoint(addr)
        tcp = TCPDispatcher(ep)
        ep.listener = tcp
        return tcp

    def get_endpoint(self,addr):

        if self.endpoints.has_key(addr):
            return self.endpoints[addr]
        else:
            conn = socket.socket(AF_INET, SOCK_STREAM)
            (ip, port) = addr
            conn.connect((ip, int(port)))
            self.endpoints[addr] = EndPoint(self, conn, addr)
            return self.endpoints[addr]

    def send(self, addr, msg):
        msg2 = (self.addr,msg)
        data = cPickle.dumps(msg2)
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
            endpoint.release()
        self.thread._Thread__stop()



class EndPoint:
    packetSizeFmt = "!I"
    packetSizeLength = struct.calcsize(packetSizeFmt)

    def __init__(self, server, epSocket,addr):
        self.socket = epSocket

        self.addr = addr
        self.server = server
        self.init = False

        self.thread = Thread(target=self._manage_socket)
        self.thread.start()

    def release(self):
        self.socket.close()
        self.thread._Thread__stop()

    def _manage_socket(self):
        try:
            self._receive_packets()
        except socket.error, e:
            self.release()

    def _receive_packets(self):
        rawPacket = self._read_incoming_packet()
        while rawPacket:
            self._dispatch_incoming_packet(rawPacket)
            rawPacket = self._read_incoming_packet()

    def _read_incoming_packet(self):
        sizeData = self._read_incoming_data(self.packetSizeLength)
        if sizeData:
            dataLength = struct.unpack(self.packetSizeFmt, sizeData)[0]
            return self._read_incoming_data(dataLength)

    def _read_incoming_data(self, dataLength):
        readBuffer = ""
        while len(readBuffer) != dataLength:
            data = self.socket.recv(dataLength - len(readBuffer))
            if not data:
                self.release()
            readBuffer += data

        return readBuffer

    def _dispatch_incoming_packet(self, rawPacket):
        msg = cPickle.loads(rawPacket)
        if not self.init:
            print msg[0]
            self.server.endpoints[msg[0]]=self
            self.init= True
        self.listener.on_message(msg[1])
        print msg


    def _send_packet(self, packetType, callID, payload):
        data = cPickle.dumps((packetType, callID, payload))
        self.socket.send(struct.pack("!I", len(data)))
        self.socket.send(data)

    def send(self,msg):
        msg2 = (self.addr,msg)
        data = cPickle.dumps(msg2)
        self.socket.send(struct.pack("!I", len(data)))
        self.socket.send(data)
