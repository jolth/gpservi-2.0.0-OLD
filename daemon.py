# -*- coding: UTF-8 -*-
#
#    Copyright (c) 2012 - 2013 Jorge A. Toro [jolthgs@gmail.com] 
#    All rights reserved.
#
#    Redistribution and use in source and binary forms, with or without
#    modification, are permitted provided that the following conditions
#    are met:
#    1. Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#    2. Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#    3. Neither the name of copyright holders nor the names of its
#       contributors may be used to endorse or promote products derived
#       from this software without specific prior written permission.
#
#    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
#    ''AS IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
#    TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
#    PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL COPYRIGHT HOLDERS OR CONTRIBUTORS
#    BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
#    CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
#    SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
#    INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
#    CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
#    ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
#    POSSIBILITY OF SUCH DAMAGE.
#
"""
    Daemons for GPS

    Usage:
    >>> import daemon
    >>> d = daemon.DaemonUDP('', 50007, 256)
    >>> d.start()
    Server run :50007
    >>> d.run()

    >>> d1 = daemon.DaemonTCP('127.0.0.1', 50009, 256)
    >>> d1.start()
    >>> d1.run()

"""
import sys
import os
import socket
import threading
from Log.logFile import createLogFile, logFile
from Load.loadconfig import load
import Devices.devices    

class DaemonUDP:
    """
        Server UDP
    """
    endfile = 0
    lock = threading.Lock()

    def __init__(self, host, port, buffering):

        self.host = host
        self.port = port
        self.buffering = buffering
        self.server = None # Servidor UDP activo 
        self.running = 1 
        self.thread = None # Hilo actual de la instacia del objeto daemon


    def start(self):
        """
            Prepara el servidor 
        """

        if createLogFile(str(load('FILELOG', 'FILE'))): # Creamos el fichero de Log
            try:
                self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Creamos el Socket Server 
                self.server.bind((self.host, self.port))
                print >> sys.stdout, ("Server run %s:%s" % (self.host, self.port))

            except socket.error, (value, message):
                if self.server:
                    self.server.close()
                print >> sys.stderr, "Could not open socket:", message
                sys.exit(1)

        
    def run(self):
        """ 
            threading 
        """
        while self.running:
            try:
                data, address = self.server.recvfrom(self.buffering) # Esperamos por un cliente UDP

                fdata = '/tmp/out'
                if os.path.exists(fdata):
                    from SendDevices import SD 
                    SD.sendData(fdata, self.server, address, data)

                self.thread = threading.Thread(target=self.threads, args=(data, address, self.__class__.lock, ))
                self.thread.start()
            except KeyboardInterrupt: 
                sys.stderr.write("\rExit, KeyboardInterrupt\n")
                try:
                    sys.stdout.write("Exit App... \n")
                    self.server.close()
                    self.thread.join() 

                    raise SystemExit("Se terminaron de ejecutar todos los dispositivos activos en el servidor")
                except AttributeError, NameError: pass

                break 



    def threads(self, data, address, lock):
        """
            run thread
        """

        print >> sys.stdout, "Data: %s|Hilo: %s" % (data, self.thread.getName())

        rawData = Devices.devices.getTypeClass(data, address) 
        
        if not rawData.has_key('id'): 
            print >> sys.stdout, rawData
            return 


        import Event.captureEvent
        event = Event.captureEvent.parseEvent(rawData) 
                                                      
        print >> sys.stdout, "Evento Gestionado: %s" % (event)

        import Log.logDB as LogDB
        LogDB.insertLog(rawData)

        lock.acquire(True)
        self.__class__.endfile = logFile(str(load('FILELOG', 'FILE')),
                                         self.__class__.endfile,
                                         raw=rawData 
                                        )
        lock.release()



class DaemonTCP:
    """
        Server TCP

    """
    def __init__(self, host, port, buffering):
        self.host = host
        self.port = port
        self.buffering = buffering
        self.server = None

    def start(self):
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
            self.server.bind((self.host,self.port)) 
            self.server.listen(5) 
            print ("Server run %s:%s" % (self.host, self.port))
        except socket.error, (value, message):
            if self.server:
                self.server.close()
            print "Could not open socket:", message 
            sys.exit(1)

        
    def run(self):
        pass
