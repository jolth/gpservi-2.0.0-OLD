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
 Módulo para el envio de e-mail
"""
import smtplib
import sys
import email.utils
from email.mime.text import MIMEText

# 
sender = 'admin@localhost'

def sendMail(receivers, subject='Simple test message', text='This is body of the message.', sender=sender, hostname='localhost'):
    """
        Usage:
            >>> import smail
            >>> 
            >>> sender = 'admin@localhost'
            >>> receivers = {'Soporte':'mail1@localhost', 'Monitoreo':'mail2@localhost'}
            >>> subject='Simple test message'
            >>> text="Este es un mensaje de prueba"
            >>> smail.sendMail(receivers, subject, text, sender)
            >>> 
    """
    msg = MIMEText(text)
    r = [(k, v) for k, v in receivers.iteritems()]
    for k in r:
        msg['To']=email.utils.formataddr(k)
    msg['From'] = email.utils.formataddr(('App Rastree', sender))
    msg['Subject'] = subject

    r = [v for v in receivers.values()]

    server = smtplib.SMTP(hostname)
    server.set_debuglevel(True) 
    try:
        server.sendmail(sender, r, msg.as_string())
        print >> sys.stderr, "**********\nSuccessfully sent email\n**********"
    except:
        print >> sys.stderr, "**********\nError: Unable to send email\n**********"
        print >> sys.stderr, sys.exc_info()
    finally:
        server.quit()
