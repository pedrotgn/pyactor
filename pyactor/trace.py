from context import init_host
from time import sleep
import pdb



class Echo:
    _tell =['echo']
    _ask = []
    def echo(self,msg):
        print msg

pdb.set_trace()
h = init_host('pedro')
e1 = h.spawn('echo1',Echo).get()
e1.echo('hola amigo !!')
sleep(1)
h.shutdown()
