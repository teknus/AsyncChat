'''
Run on python3.5 

'''
from socket import socket, SO_REUSEADDR, SOL_SOCKET
from asyncio import Task, get_event_loop

class Peer(object):
    def __init__(self, server, sock, name):
        self.loop = server.loop
        self.name = name
        self._sock = sock
        self._server = server
        self.online_channel = "NoneConnection\n"
        Task(self._peer_handler())

    def send(self, data):
        return self.loop.sock_sendall(self._sock, data.encode('utf8'))
    
    async def _peer_handler(self):
        try:
            await self._peer_loop()
        except Exception:
            self._server.leave_channel(self,self.online_channel)

    async def _peer_loop(self):
        while True:
            buf = await self.loop.sock_recv(self._sock, 1024)
            if '/create' in str(buf.decode()):
                if self._server.create_channel(str(str(buf.decode()).split(" ")[1]), self):
                    self._server.enter_in_channel(str(str(buf.decode()).split(" ")[1]), self)
                    self.online_channel = str(str(buf.decode()).split(" ")[1])
                    self._server._channels["NoneConnection\n"].remove(self)
            elif "/join" in str(buf.decode()):
                self._server.enter_in_channel(str(str(buf.decode()).split(" ")[1]), self)
                self.online_channel = str(str(buf.decode()).split(" ")[1])
                self._server.leave_channel(self, 'NoneConnection\n')
            elif "/out" in str(buf.decode()):
                self._server.enter_in_channel('NoneConnection\n', self)
                self._server.leave_channel(self, self.online_channel)
                self.online_channel = 'NoneConnection\n'
            elif "/whereami" in str(buf.decode()):
                self._server.echo("{}\n".format(self.online_channel),self)
                print(self.online_channel)
            elif "/list" in str(buf.decode()):
                chn = "\nList of open channels \n"+"".join(self._server.all_channels()) + "\n"
                self._server.echo(chn, self)
            else:
                if self.online_channel != "NoneConnection\n":
                    self._server.broadcast('{}: {}'.format(self.name.decode(), buf.decode('utf8')),self)

    def get_sock(self):
        return self._sock

    def __eq__(self, other):
        return self._sock == other.get_sock()

class Server(object):
    def __init__(self, loop, port):
        self.loop = loop
        self._serv_sock = socket()
        self._serv_sock.setblocking(0)
        self._serv_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self._serv_sock.bind(('',port))
        self._serv_sock.listen(5)
        self._peers = []
        self._channels = {'NoneConnection\n':list()}
        Task(self._server())

    def leave_channel(self, peer,chan):
        self._channels[chan].remove(peer)
        self.broadcast_chan('Peer {} quit from {}!\n'.format(peer.name.decode(),chan), peer, chan)

    def broadcast(self, message, peer):
        for p in self._peers:
            if p != peer:
                p.send(message)

    def echo(self, message, peer):
        i = 0
        for p in self._peers:
            if p == peer and i == 0:
                p.send(message)
                i += 1

    def broadcast_chan(self, message, peer, chan):
        for p in self._channels[chan]:
            if p != peer:
                p.send(message)

    def enter_in_channel(self, chan, peer):
        try:
            self._channels[chan].append(peer)
            self.broadcast_chan("User {} connected in {}".format(peer.name.decode(),chan), peer, chan)
            self.echo("Connected in {}".format(chan),peer)
        except KeyError:
            peer.echo("There is no channel {}".format(chan),peer)

    def create_channel(self, chan, peer):
        for ch in self._channels.keys():
            if ch == chan:
                peer.echo("The {} channel already exists".format(chan),peer)
                return False
        self._channels[chan] = []
        print(self._channels.keys())
        return True

    def all_channels(self):
        return [x for x in self._channels.keys()]

    async def _server(self):
        while True:
            peer_sock, peer_name = await self.loop.sock_accept(self._serv_sock)
            name = await self.loop.sock_recv(peer_sock, 1024)
            peer_sock.setblocking(0)
            peer = Peer(self, peer_sock, name)
            self._channels['NoneConnection\n'].append(peer)
            self._peers.append(peer)
            #self.broadcast_chan('Peer {} connected!\n'.format(name.decode()),user,'NoneConnection\n')
            self.echo("commands\n/join <nome do canal>\n/create <nome do canal>\n/out <sair canal>\n/whereami\n/list\n",peer)

def main():
    loop = get_event_loop()
    Server(loop, 1234)
    loop.run_forever()

if __name__ == '__main__':
    main()