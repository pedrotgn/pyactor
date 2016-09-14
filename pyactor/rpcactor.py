import uuid

from pyactor.thread.actor import Actor, Channel
from util import *
from urlparse import urlparse
from rpcserver import *


class RPCDispatcher(Actor):

    def __init__(self, url):
        self.url = url
        aurl = urlparse(url)
        address = aurl.netloc.split(':')
        ip, port = address[0], address[1]
        self.source = Source((ip, int(port)))
        self.source.register_function(self.on_message)
        self.source.start()
        self.running = True
        self.channel = Channel()
        self.pending = {}   # Sended to another host
        self.executing = {}  # Waiting for the response in this server
        self.tell = ['stop']
        self.ask = []
        self.ask_ref = []
        self.tell_ref = []
        self.sinks = {}

    def get_sink(self, url):
        if url in self.sinks.keys():
            return self.sinks[url]
        else:
            self.sinks[url] = Sink(url)
            return self.sinks[url]

    def receive(self, msg):
        if msg[TYPE] == TELL and msg[METHOD] == 'stop':
                self.running = False
                self.source.stop()
        else:
            try:
                if msg[TYPE] == TELL:
                    self.get_sink(msg[TO]).send(msg)
                elif msg[TYPE] == ASK:
                    rpc_id = str(uuid.uuid4())
                    msg[RPC_ID] = rpc_id
                    self.pending[rpc_id] = msg[CHANNEL]
                    del msg[CHANNEL]
                    msg[FROM] = self.url
                    self.get_sink(msg[TO]).send(msg)
                elif msg[TYPE] == ASKRESPONSE:
                    # print msg
                    if msg[RPC_ID] in self.executing.keys():
                        self.get_sink(self.executing[msg[RPC_ID]]).send(msg)
                        del self.executing[msg[RPC_ID]]
            except Exception as e:
                print e

    def on_message(self, msg):
        try:
            if msg[TYPE] == TELL:
                get_host().actors[msg[TO]].channel.send(msg)
            elif msg[TYPE] == ASK:
                # print msg
                # Save rpc id and actor channel
                rpc_id = msg[RPC_ID]
                self.executing[rpc_id] = msg[FROM]
                # Change msg callback channel, add id
                msg[CHANNEL] = self.channel
                get_host().actors[msg[TO]].channel.send(msg)
            elif msg[TYPE] == ASKRESPONSE:
                # print msg
                if msg[RPC_ID] in self.pending.keys():
                    self.pending[msg[RPC_ID]].send(msg)
                    del self.pending[msg[RPC_ID]]
        except Exception, e:
            print 'TCP ERROR:', e, 'does not exist?'
