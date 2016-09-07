from pyactor.util import TimeoutError


k = 7
MAX = 2 ** k


def decr(value, size):
    if size <= value:
        return value - size
    else:
        return MAX - (size - value)


# ---------BETWEEN---------
def between(value, init, end):
    if init == end:
        return True
    elif init > end:
        shift = MAX - init
        init = 0
        end = (end + shift) % MAX
        value = (value + shift) % MAX
    return init < value < end


def Ebetween(value, init, end):
    if value == init:
        return True
    else:
        return between(value, init, end)


def betweenE(value, init, end):
    if value == end:
        return True
    else:
        return between(value, init, end)
# -------END_BETWEEN-------


def update(ref):
    ref.stabilize()
    ref.fix_finger()


def exit1(ref):
    ref.leave()


def show(ref):
    ref.show_finger_node()


class SuccessorError(Exception):
    def __str__(self):
        return 'The successor is down'


class Node(object):
    _ask = ['init_node', 'successor', 'find_successor', 'get_predecessor',
            'closest_preceding_finger', 'join', 'is_alive', 'find_predecessor',
            'get_finger']
    _tell = ['leave', 'set_predecessor', 'set_successor', 'show_finger_node',
             'stabilize', 'notify', 'fix_finger']
    _ref = ['set_predecessor', 'get_predecessor', 'successor',
            'find_successor', 'closest_preceding_finger', 'join',
            'set_successor', 'notify', 'get_finger', 'find_predecessor']
    _parallel = ['stabilize', 'fix_finger', 'find_predecessor',
                 'find_successor']

    def __init__(self):
        self.finger = {}
        self.start = {}
        self.indexLSucc = 0
        self.currentFinger = 1

    def init_node(self):
        for i in range(k):
            self.start[i] = (long(self.id) + (2 ** i)) % (2 ** k)
        return True

    def successor(self):
        return self.finger[0]

    def find_successor(self, nid):
        try:
            if betweenE(nid, long(self.predecessor.get_id()), long(self.id)):
                return self.proxy
            n = self.proxy.find_predecessor(nid, timeout=2)
            return n.successor(timeout=2)
        except TimeoutError, e:
            raise e

    def get_predecessor(self):
        return self.predecessor

    def set_predecessor(self, pred):
        self.predecessor = pred

    # Iterative programming
    def find_predecessor(self, nid):
        try:
            if nid == long(self.id):
                return self.predecessor
            n1 = self.proxy
            while not betweenE(nid, long(n1.get_id()),
                               long(n1.successor(timeout=2).get_id())):
                n1 = n1.closest_preceding_finger(nid, timeout=2)
            return n1
        except SuccessorError, e:
            raise e
        except TimeoutError, e:
            raise e

    def closest_preceding_finger(self, nid):
        try:
            for i in range(k - 1, -1, -1):
                if between(long(self.finger[i].get_id()), long(self.id), nid):
                    return self.finger[i]
            return self.proxy
        except(TimeoutError):
            raise SuccessorError()

    def join(self, n1):
        """if join returns false, the node did not entry the ring. Retry it"""
        if self.id == n1.get_id():
            for i in range(k):
                self.finger[i] = self.proxy
            self.predecessor = self.proxy
            self.run = True
            return True
        else:
            try:
                self.init_finger_table(n1)
            except Exception:
                print 'Join failed'
                # raise Exception('Join failed')
                return False
            else:
                self.run = True
                return True

    def init_finger_table(self, n1):
        try:
            self.finger[0] = n1.find_successor(self.start[0], timeout=5)
            self.predecessor = self.finger[0].get_predecessor(timeout=2)
        except SuccessorError, e:
            raise e
        except TimeoutError, e:
            raise e
        else:
            # neighbor_finger = self.finger[0].get_finger(timeout=2)
            # for i in range(k - 1):
            #     self.finger[i + 1] = neighbor_finger[i]
            for i in range(k - 1):
                self.finger[i + 1] = self.finger[0]

    def is_alive(self):
        if self.run:
            return True
        else:
            return False

    def stabilize(self):
        try:
            x = self.finger[0].get_predecessor(timeout=2)
        except Exception:
            pass
        else:
            if (between(long(x.get_id()), long(self.id),
                        long(self.finger[0].get_id()))):
                self.set_successor(x)
            self.finger[0].notify(self.proxy)

    def notify(self, n):
        if(self.predecessor.get_id() == self.id or
           between(long(n.get_id()), long(self.predecessor.get_id()),
                   long(self.id))):
            self.predecessor = n

    def fix_finger(self):
        # try:
        #     for i in range(4):
        #         if(self.currentFinger <= 0 or self.currentFinger >= k ):
        #             self.currentFinger = 1
        #         self.finger[self.currentFinger] = self.proxy.find_successor(
        #                             self.start[self.currentFinger], timeout=5)
        #         self.currentFinger += 1
        # except Exception:
        #     pass
        try:
            if(self.currentFinger <= 0 or self.currentFinger >= k):
                self.currentFinger = 1
            self.finger[self.currentFinger] = self.proxy.find_successor(
                                    self.start[self.currentFinger], timeout=5)
        except:
            pass
        else:
            self.currentFinger += 1

    def get_finger(self):
        return self.finger.values()

    def leave(self):
        print 'bye bye!'
        self.finger[0].set_predecessor(self.predecessor)
        self.predecessor.set_successor(self.finger[0])
        self.proxy.stop()

    def set_successor(self, succ):
        self.finger[0] = succ

    def show_finger_node(self):
        print 'Finger table of node ' + self.id
        print 'Predecessor ' + self.predecessor.get_id()
        print 'start: node'
        for i in range(k):
            print str(self.start[i]) + ' : ' + self.finger[i].get_id()
        print '-----------'
