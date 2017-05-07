# telnet program example
from __future__ import print_function

import socket, select, string, sys, os

def prompt(name) :
    sys.stdout.write(name)
    sys.stdout.flush()
 
#main function
if __name__ == "__main__":
     
    if(len(sys.argv) < 3) :
        print ('Usage : python telnet.py hostname port')
        sys.exit()

    name = input("say my name: ")
    name = "<{}>".format(name)
    host = sys.argv[1]
    port = int(sys.argv[2])
     
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
     
    # connect to remote host
    try :
        s.connect((host, port))
    except :
        print ('Unable to connect')
        sys.exit()
    s.send(name.encode())
     
    print( 'Connected to remote host. Start sending messages')
    prompt(name)
     
    while 1:
        socket_list = [sys.stdin, s]
         
        # Get the list sockets which are readable
        read_sockets, write_sockets, error_sockets = select.select(socket_list , [], [])
         
        for sock in read_sockets:
            #incoming message from remote server
            if sock == s:
                data = sock.recv(4096)
                if not data :
                    print ('\nDisconnected from chat server')
                    sys.exit()
                else :
                    #print data
                    sys.stdout.write(data.decode())
                    prompt(name)
             
            #user entered a message
            else :
                msg = sys.stdin.readline()
                s.send(msg.encode())
                prompt(name)