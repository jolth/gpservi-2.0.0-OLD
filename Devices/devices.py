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
import sys
import datetime
import StringIO
from UserDict import UserDict
import simplejson as json
from Gps.Antares.convert import latWgs84ToDecimal, lngWgs84ToDecimal
from Gps.Antares.secondsTohours import secTohr 
from Gps.SkyPatrol.convert import degTodms, skpDate, skpTime, fechaHoraSkp
from Gps.common import MphToKph, NodeToKph
from Gps.common import ignitionState, ignitionStatett8750  
import Location.geomapgoogle
import Location.geocoding


def tagData(dFile, position, bit=None, seek=0):
    """
        Toma un punto de partida (position), cantidad de bit y un punto de 
        referencia para leer los bit(según el método seek() de los fichero).
        Además dataFile el cual es objeto StringIO.
    """
    try:
        dFile.seek(position, seek)
        tagdata =  dFile.read(bit)
    except: sys.stderr.write("Error al obtener el Tag Data")
            
    return tagdata


# Clase que actua como un diccionario
class Device(UserDict):
    """ Store Device"""
    def __init__(self, deviceData=None, address=None):
        UserDict.__init__(self)
        self["data"] = deviceData
        self["address"] = "%s,%s" % address


class ANTDevice(Device):
    """
        Dispositivo Antares
    """
    tagDataANT = {  
                    "id"        : (-6, None, 2, tagData, None), # ID de la unidad
                    "type"      : (0, 1, 0, tagData, None),
                    "typeEvent" : (1, 2, 0, tagData, None),     # 
                    "codEvent"  : (3, 2, 0, tagData, None),     # Codigo de evento activado (en Antares de 00 a 49, en e.Track de 00 a 99)
                    "weeks"     : (5, 4, 0, tagData, None),     # Es el numero de semanas desde 00:00AM del 6 de enero de 1980.
                    "dayWeek"   : (9, 1, 0, tagData, None),     # 0=Domingo, 1=Lunes, etc hasta 6=sabado.
                    #"time"      : (10, 5, 0, tagData, None),    # Hora expresada en segundos desde 00:00:00AM
                    "secondsDay"      : (10, 5, 0, tagData, None),    # Hora expresada en segundos desde 00:00:00AM
                    "time"      : (10, 5, 0, tagData, secTohr),    # Hora expresada en segundos desde 00:00:00AM
                    "lat"       : (15, 8, 0, tagData, latWgs84ToDecimal),    # Latitud
                    "lng"       : (23, 9, 0, tagData, lngWgs84ToDecimal),    # Longitud
                    "speed"     : (-18, 3, 2, tagData, MphToKph),   # Velocidad en MPH
                    "course"    : (-15, 3, 2, tagData, None),   # Curso en grados
                    "gpsSource" : (-12, 1, 2, tagData, None),   # Fuente GPS. Puede ser 0=2D GPS, 1=3D GPS, 2=2D DGPS, 3=3D DGPS, 6=DR, 8=Degraded DR.     
                    "ageData"   : (-11, 1, 2, tagData, None)    # Edad del dato. Puede ser 0=No disponible, 1=viejo (10 segundos) ó 2=Fresco (menor a 10 segundos)
                 }


    def __parse(self, data):
        self.clear()
        try:
            dataFile = StringIO.StringIO(data[1:-1]) # remove '<' y '>'
            #
            for tag, (position, bit, seek, parseFunc, convertFunc) in self.tagDataANT.items():
                self[tag] = convertFunc and convertFunc(parseFunc(dataFile, position, bit, seek)) or parseFunc(dataFile, position, bit, seek)

            # Creamos una key para la altura (estandar), ya que las tramas actuales no la incluyen:
            self['altura'] = None
            # Creamos una key para el dato position:
            self['position'] = "(%(lat)s,%(lng)s)" % self

            self["datetime"] = datetime.datetime.fromtimestamp((315964800000 + ((int(self['weeks'])* 7 + int(self['dayWeek'])) * 24 * 60 * 60 + int(self['secondsDay'])) * 1000) // 1000) 
            
            # Realizamos la Geocodificación.
            self["geocoding"] = None 
            self["geocoding"] = Location.geocoding.regeocodeOSM('%s,%s' % (self["lat"], self["lng"]))

        except: print(sys.exc_info()) #sys.stderr.write('Error Inesperado:', sys.exc_info())
        #finally: dataFile.close()


    def __setitem__(self, key, item):
        if key == "data" and item:
            self.__parse(item)

        Device.__setitem__(self, key, item) 

        
def tagDataskp(dList, start, end, name):
    """
        Toma una posición para obtener la lista dList.
    """
    try:
        if end: 
            tagdata = dList[start:end + 1]
        else:
            tagdata = dList[start]
    except: sys.stderr.write("Error al obtener el Tag Data: %s, %s. Evento: %s.\n" % (name, dList[3], dList[2])) 
            
    return tagdata or None
    

class SKPDevice(Device):
    """
        Dispositivo Skypatrol
    """
    tagDataSKP = {  
                    "id"        : (3, None, tagDataskp, 'id', None), # ID de la unidad
                    "type"      : (0, None, tagDataskp, 'type', None),
                    "typeEvent" : (5, None, tagDataskp, 'typeEvent', None), # 
                    "ignition"  : (4, None, tagDataskp, 'ignition', ignitionState), # 

                    "codEvent"  : (2, None, tagDataskp, 'codEvent', None), # Codigo de evento activado (en Antares de 00 a 49, en e.Track de 00 a 99)
                    "weeks"     : (0, None, tagDataskp, 'weeks', None), # Es el numero de semanas desde 00:00AM del 6 de enero de 1980.
                    "dayWeek"   : (0, None, tagDataskp, 'dayWeek', None), # 0=Domingo, 1=Lunes, etc hasta 6=sabado.
                    "time"      : (6, None, tagDataskp, 'time', skpTime), # Hora expresada en segundos desde 00:00:00AM
                    "lat"       : (8, 9, tagDataskp, 'lat', degTodms), # Latitud
                    #"lat"       : (6, tagDataskp, latWgs84ToDecimal),    # Latitud
                    "lng"       : (10, 11, tagDataskp, 'lng', degTodms), # Longitud
                    #"lng"       : (23, 9, 0, tagDataskp, lngWgs84ToDecimal),    # Longitud
                    "speed"     : (12, None, tagDataskp, 'speed', NodeToKph),   # Velocidad en MPH
                    "course"    : (13, None, tagDataskp, 'course', None), # Curso en grados
                    "gpsSource" : (0, None, tagDataskp, 'gpsSource', None), # Fuente GPS. Puede ser 0=2D GPS, 1=3D GPS, 2=2D DGPS, 3=3D DGPS, 6=DR, 8=Degraded DR. # Problema DB si no son enteros    
                    "ageData"   : (0, None, tagDataskp, 'ageData', None), # Edad del dato. Puede ser 0=No disponible, 1=viejo (10 segundos) ó 2=Fresco (menor a 10 segundos) # Problema DB si no son enteros
                    "date"  : (14, None, tagDataskp, 'date', skpDate), # Fecha 
                    "odometro"  : (15, None, tagDataskp, 'odometro', None) # Odómetro
                 }


    def __parse(self, data):
        self.clear()
        try:
            import re

            data = data.replace(' ', ',')
            dataList = [i for i in data.split(',') if i]
            dataList.insert(0, '')
            for tag, (position_start, position_end, parseFunc, nameTag, convertFunc) in self.tagDataSKP.items():
                self[tag] = convertFunc and convertFunc(parseFunc(dataList, position_start, position_end, nameTag)) or parseFunc(dataList, position_start, position_end, nameTag)

            # Creamos una key para la altura (estandar), ya que las tramas actuales no la incluyen:
            self['altura'] = None
            # Creamos una key para el dato position:
            self['position'] = "(%(lat)s,%(lng)s)" % self

            # Fecha y Hora del dispositivo:
            self["datetime"] = fechaHoraSkp(self["date"], self["time"]) 

            # Realizamos la Geocodificación.
            self["geocoding"] = None 
            self["geocoding"] = Location.geocoding.regeocodeOSM('%s,%s' % (self["lat"], self["lng"]))


        except: print(sys.exc_info()) #sys.stderr.write('Error Inesperado:', sys.exc_info())
        #finally: dataFile.close()


    def __setitem__(self, key, item):
        if key == "data" and item:
            self.__parse(item)
        # Llamamos a __setitem__ de nuestro ancestro
        Device.__setitem__(self, key, item) 


class TTDevice(Device):
    """
        Dispositivo Skypatrol TT8750
    """
    tagDataSKP = {  
                    "id"        : (3, None, tagDataskp, 'id', None), # ID de la unidad
                    "type"      : (0, None, tagDataskp, 'type', None),
                    "typeEvent" : (4, None, tagDataskp, 'typeEvent', None), # 
                    "ignition"  : (5, None, tagDataskp, 'ignition', ignitionStatett8750), # 

                    "codEvent"  : (2, None, tagDataskp, 'codEvent', None), # Codigo de evento activado (en Antares de 00 a 49, en e.Track de 00 a 99)
                    "weeks"     : (0, None, tagDataskp, 'weeks', None), # Es el numero de semanas desde 00:00AM del 6 de enero de 1980.
                    "dayWeek"   : (0, None, tagDataskp, 'dayWeek', None), # 0=Domingo, 1=Lunes, etc hasta 6=sabado.
                    "time"      : (7, None, tagDataskp, 'time', skpTime), # Hora expresada en segundos desde 00:00:00AM
                    "lat"       : (9, 10, tagDataskp, 'lat', degTodms), # Latitud
                    #"lat"       : (6, tagDataskp, latWgs84ToDecimal),    # Latitud
                    "lng"       : (11, 12, tagDataskp, 'lng', degTodms), # Longitud
                    #"lng"       : (23, 9, 0, tagDataskp, lngWgs84ToDecimal),    # Longitud
                    "speed"     : (13, None, tagDataskp, 'speed', NodeToKph),   # Velocidad en MPH
                    "course"    : (14, None, tagDataskp, 'course', None), # Curso en grados
                    "gpsSource" : (0, None, tagDataskp, 'gpsSource', None), # Fuente GPS. Puede ser 0=2D GPS, 1=3D GPS, 2=2D DGPS, 3=3D DGPS, 6=DR, 8=Degraded DR. # Problema DB si no son enteros    
                    "ageData"   : (0, None, tagDataskp, 'ageData', None), # Edad del dato. Puede ser 0=No disponible, 1=viejo (10 segundos) ó 2=Fresco (menor a 10 segundos) # Problema DB si no son enteros
                    "date"  : (15, None, tagDataskp, 'date', skpDate), # Fecha 
                    "odometro"  : (16, None, tagDataskp, 'odometro', None) # Odómetro
                 }


    def __parse(self, data):
        self.clear()
        try:
            import re

            data = data.replace(' ', ',')
            dataList = [i for i in data.split(',') if i]
            dataList.insert(0, '')
            for tag, (position_start, position_end, parseFunc, nameTag, convertFunc) in self.tagDataSKP.items():
                self[tag] = convertFunc and convertFunc(parseFunc(dataList, position_start, position_end, nameTag)) or parseFunc(dataList, position_start, position_end, nameTag)

            # Creamos una key para la altura (estandar), ya que las tramas actuales no la incluyen:
            self['altura'] = None
            # Creamos una key para el dato position:
            self['position'] = "(%(lat)s,%(lng)s)" % self

            # Fecha y Hora del dispositivo:
            self["datetime"] = fechaHoraSkp(self["date"], self["time"]) 

            # Realizamos la Geocodificación.
            self["geocoding"] = None 
            self["geocoding"] = Location.geocoding.regeocodeOSM('%s,%s' % (self["lat"], self["lng"]))


        except: print(sys.exc_info()) #sys.stderr.write('Error Inesperado:', sys.exc_info())
        #finally: dataFile.close()


    def __setitem__(self, key, item):
        if key == "data" and item:
            self.__parse(item)
        # Llamamos a __setitem__ de nuestro ancestro
        Device.__setitem__(self, key, item) 


class HUNTDevice(Device):
    """
        Dispositivo Hunter
    """
    pass



def typeDevice(data):
    """
        Determina que tipo de Dispositivo GPS es dueña de la data.

        Usage:
            >>> import devices
            >>> 
            >>> data='>REV041674684322+0481126-0757378200000012;ID=ANT001<'
            >>> devices.typeDevice(data)
            'ANT'
            >>>
            >>> type(devices.typeDevice(''))
            <type 'NoneType'>
            >>>
            >>> if devices.typeDevice('') is not None: print "Seguir con el programa..."
            ... 
            >>> if devices.typeDevice(data) is not None: print "Seguir con el programa..."
            ... 
            Seguir con el programa...
            >>> 
    """
    # Dispositivos soportados:
    types = ('ANT', 'SKP', 'TT')

    typeDev = lambda dat: ("".join(
                            [d for d in types 
                            if dat.find(d) is not -1])
                        )
    return typeDev(data) or None #raise


def getTypeClass(data, address=None, module=sys.modules[Device.__module__]):
    """
        Determina que clase debe manejar un determinado dispositivo y
        retorna un diccionario con la trama procesada.

        Recibe la data enviada por el dispositivo (data), y opcionalmente 
        el nombre del módulo donde se encuentra la clase que manipula este 
        tipo de dispositivo (module). La clase manejador debe tener un 
        formato compuesto por 'TIPO_DISPOSITIVO + Device' por ejemplo: ANTDevice,
        SKPDevice, etc.

        Usage:
            >>> import devices
            >>> 
            >>> data='>REV001447147509+2578250-0802813901519512;ID=ANT001<'
            >>> devices.getTypeClass(data)
            {'codEvent': '00', 'weeks': '1447', 'dayWeek': '1', 'ageData': '2', \
            'type': 'R', 'data': '>REV001447147509+2578250-0802813901519512;ID=ANT001<', \
            'course': '195', 'gpsSource': '1', 'time': '47509', 'lat': '+2578250', \
            'typeEvent': 'EV', 'lng': '-08028139', 'speed': '015', 'id': 'ANT001'}
            >>> print "\n".join(["%s=%s" % (key,value) for key, value in devices.getTypeClass(data).items()])
            codEvent=00
            weeks=1447
            dayWeek=1
            ageData=2
            type=R
            data=>REV001447147509+2578250-0802813901519512;ID=ANT001<
            course=195
            gpsSource=1
            time=47509
            lat=+2578250
            typeEvent=EV
            lng=-08028139
            speed=015
            id=ANT001
            >>> 
    """
    import re

    data = re.sub(r"[\r\n]+", "", data)

    # Determinamos la clase manejadora adecuado según el dispositivo
    dev = "%sDevice" % typeDevice(data)

    def getClass(module, dev): 
        """ 
            Retorna una referencia a la clase manejadora. 
            Usage:
            >>> getClass(module, 'ANTDevice')
            <class devices.ANTDevice at 0xb740435c>
            >>> getClass(module, 'SKPDevice')
            <class devices.SKPDevice at 0xb740438c>
            >>> getClass(module, '')
            <class devices.Device at 0xb740426c>
            >>> 
        """
        return hasattr(module, dev) and getattr(module, dev) or Device

    return getClass(module, dev)(data, address)

