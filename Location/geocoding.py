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
"""
    Geocoding API Google/OSM

    Usage: 
        >>> import geocoding
        >>>
        >>> geocoding.geocodeGMap('Manizales')
        '["Manizales, Caldas, Colombia", "Manizales, Caldas, Colombia"]'
        >>>
        >>> geocoding.regeocodeGMap('5.06889,-75.51738')
        '["Carrera 20 # 22-1 a 22-99, Manizales, Caldas, Colombia", "Manizales, Caldas, Colombia", "Caldas, Colombia", "Colombia"]'
        >>>
"""
import urllib, json

#GEOCODE_BASE_URL = 'http://maps.google.com/maps/api/geocode/json'
GEOCODE_BASE_URL = 'http://maps.googleapis.com/maps/api/geocode/json'
REGEOCODE_BASE_URL = 'http://maps.google.com/maps/geo'
OSM_REGEOCODE_BASE_URL = 'http://nominatim.openstreetmap.org/reverse'

def geocodeGMap(address, sensor='false', **geo_args):
    """
        Geocoding Google Map
    """
    geo_args = ({
        'address': address,
        'sensor': sensor
    })

    url = GEOCODE_BASE_URL + '?' + urllib.urlencode(geo_args)
    result = json.load(urllib.urlopen(url))
    return json.dumps([s['formatted_address']
                       for s in result['results']])

def regeocodeGMapOLD(latlng, sensor='false', **geo_args):
    """
        Google Map Reverse Geocoding 
        URL: http://maps.google.com/maps/geo?q=5.06889,-75.51738&output=json&sensor=false
    """
    geo_args = ({
        'key' : '', # debe poner su clade de API Google Map
        'q' : latlng,
        'output' : 'json',
        'sensor' : sensor
    })

    url = REGEOCODE_BASE_URL + '?' + urllib.unquote(urllib.urlencode(geo_args))
    result = json.load(urllib.urlopen(url))

    return json.dumps([s['address'] 
               for s in result['Placemark']])


def regeocodeGMap(latlng, level=None, sensor='false', **geo_args):
    """
        Google Map Reverse Geocoding
            
            Por defecto level se pone a 0. Lo cual nos muestra la 
            ubicación con el maximo detalle.

        Usage:
            >>> geocoding.regeocodeGMap('5.06889,-75.51738')
            u'Carrera 20 # 22-1 a 22-99, Manizales, Caldas, Colombia'
            >>> geocoding.regeocodeGMap('5.06889,-75.51738', 1)
            u'Manizales, Caldas, Colombia'
            >>> geocoding.regeocodeGMap('5.06889,-75.51738', 2)
            u'Caldas, Colombia'
            >>> geocoding.regeocodeGMap('5.06889,-75.51738', 3)
            u'Colombia'
            >>>
    """
    geo_args = ({
        'latlng' : latlng,
        'sensor' : sensor
    })

    url = GEOCODE_BASE_URL + '?' + urllib.unquote(urllib.urlencode(geo_args))
    result = json.load(urllib.urlopen(url))
    return level and json.loads(json.dumps([s['formatted_address'] 
           for s in result['results']]))[level] or json.loads(json.dumps([s['formatted_address']
               for s in result['results']]))[0]


def regeocodeOSM(latlng, **geo_args):
    """
        OSM Reverse Geocoding

        usage:
        >>> geocoding.regeocodeOSM('5.03515676667,-75.4606770833')
        u'50, Parque Industrial Juanchito, Tesorito, Comuna Tesorito, Manizales, Centrosur, Caldas, 170003, Colombia'
        >>>
    """
    latlng = latlng.split(',')

    geo_args = ({
        'format' : 'json',
        'lat'  : latlng[0],
        'lon' : latlng[1],
        'zoom'  : 18,
        'addressdetails'  : 1,
        'email'  : 'jorge.toro@devmicrosystem.com'.encode("utf8")
    })

    url = OSM_REGEOCODE_BASE_URL + '?' + urllib.unquote(urllib.urlencode(geo_args))
    result = json.load(urllib.urlopen(url))

    return result['display_name']

