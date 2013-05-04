# -*- coding: utf-8 -*-
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
from pytz import timezone

def deg_to_dms(num, signo):       
    """
    """
    point = num.find('.')
    d = num[:point-2]
    m = num[point-2:]
    m = float(m) / 60
    numero = float(d) + m
    if signo in ['S','W']:
        return numero * (-1)
    return numero


def degTodms(s):       
    """
    """
    num = s[0]
    signo = s[1]
    point = num.find('.')
    d = num[:point-2]
    m = num[point-2:]
    m = float(m) / 60
    numero = float(d) + m
    if signo in ['S','W']:
        return numero * (-1)
    return numero


def skpDate(date):
    """
        Retorna un date con la fecha en que la unidad genero la trama.

        >>> date = '041212'
        >>> datetime.date(2000 + int(date[4:6]), int(date[2:4]), int(date[0:2])) 
        datetime.date(2012, 12, 4)
        >>>
    """
    import datetime
    return datetime.date(2000 + int(date[4:6]), int(date[2:4]), int(date[0:2]))

def skpTime(time):
    """
        Retorna un time con la hora en que la unidad genero la trama.

        >>> time = '212753.00'
        >>> datetime.time(int(time[0:2]), int(time[2:4]), int(time[4:6]), int(time[-2]))
        datetime.time(21, 27, 53)
        >>> 
    """
    import datetime
    return datetime.time(int(time[0:2]), int(time[2:4]), int(time[4:6]), int(time[-2]), tzinfo=timezone('UTC')) 

def fechaHoraSkp(date, time):
    """
        Crea un datetime para la fecha y la hora en que la unidad 
        genero la trama.

        >>> from datetime import datetime
        >>> from pytz import timezone
        >>>
        >>> d1 = date(2012, 12, 4)
        >>> d2 = time(21, 27, 53, tzinfo=timezone('UTC'))
        >>> d3 = datetime.combine(d1, d2)
        >>> d3
        datetime.datetime(2012, 12, 4, 21, 27, 53, tzinfo=<UTC>)
        >>> d3.astimezone(timezone('America/Bogota'))
        datetime.datetime(2012, 12, 4, 16, 27, 53, tzinfo=<DstTzInfo 'America/Bogota' COT-1 day, 19:00:00 STD>)
        >>>

    """
    from datetime import datetime
    from Load.loadconfig import load
    utc = load('CONFIGURE', 'UTC')
    dt = datetime.combine(date, time)
    return dt.astimezone(timezone(str(utc)))
