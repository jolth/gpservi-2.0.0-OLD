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
import os
import sys
from datetime import datetime

class sendData:
    """
    """
    def __init__(self, f, server, address, data):
        self.data = data
        self.file = f
        with open(self.file, 'r') as f:
            self.device = f.readline().replace('\n', '');

        if data.find(self.device) is not -1:
           print "#################  Device a Enviar Data:", self.device 
           self.send(server, address)
            
        
    def send(self, server, address): 
        with open(self.file, 'r') as f:
            f.readline()
            s = 0
            for l in f:
                print >>sys.stderr, '<-' * 34
                print >>sys.stderr, 'Fecha: %s' % datetime.now()
                print >>sys.stderr, 'ID: %s' % self.device
                print >>sys.stderr, 'IP/Port: %s/%s' % (address[0], address[1])
                d = '\x00\x01\x04\x00 ' + l
                sent = server.sendto(d, address)
                print >>sys.stderr, 'Sending: "%s"' % l 

        os.remove(self.file)

        # Receive response
        print >>sys.stderr, 'Waiting to Receive:\n'
        d, s = server.recvfrom(4096)
        print >>sys.stderr, d
        print >>sys.stderr, '->' * 34
