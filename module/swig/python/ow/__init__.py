"""
::BOH
$Id$
$HeadURL: http://subversion/stuff/svn/owfs/trunk/ow/__init__.py $

Copyright (c) 2004, 2005 Peter Kropf. All rights reserved.

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or (at
your option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
::EOH

1-wire sensor network interface.

OWFS is an open source project developed by Paul Alfille and hosted at
http://owfs.sourceforge.net.
"""


import os
import _OW


__author__ = 'Peter Kropf'
__email__ = 'peterk at bayarea dot net'
__version__ = _OW.version( ) + '-%s' % '$Id$'.split( )[ 2 ]


#
# Exceptions used and thrown by the ow classes
#

class exError( Exception ):
    """Base exception for all one wire raised exceptions."""


class exErrorValue( exError ):
    """Base exception for all one wire raised exceptions with a value."""
    def __init__( self, value ):
        self.value = value

    def __str__( self ):
        return repr( self.value )


class exNoController( exError ):
    """Exception raised when a controller cannot be initialized."""


class exNotInitialized( exError ):
    """Exception raised when a controller has not been initialized."""


class exPath( exErrorValue ):
    """Exception raised when a specified path doesn't exist."""


class exAttr( exErrorValue ):
    """Exception raised when a sensor attribute doesn't exist."""


#
# Module variable used to insure that the _OW library has been
# initialized before any calls into it are made.
#

initialized = False


#
# Module varialbe used to turn on _OW function call logging
#

use_logging = False
#use_logging = True


def log_get( path ):
    """
    Write the _OW.get call details out to the log file.
    """
    logfile.write( "_OW.get( '%s' )%s" % ( path, os.linesep ) )
    return _OW.get( path )


def log_put( path, value ):
    """
    Write the _OW.put call details out to the log file.
    """
    logfile.write( "_OW.put( '%s', '%s' )%s" % ( path, value, os.linesep ) )
    return _OW.put( path, value )


if use_logging:
    logfile = open( 'OW.log', 'w' )
    owfs_get = log_get
    owfs_put = log_put
else:
    owfs_get = _OW.get
    owfs_put = _OW.put


#
# Initialize and cleanup the _OW library.
#

def init( iface ):
    """
    Initialize the OWFS library by specifying the interface mechanism
    to be used for communications to the 1-wire network.

    Examples:

        ow.init( 'u' )

    Will initialize the 1-wire interface to use the USB controller.

        ow.init( '/dev/ttyS0' )

    Will initialize the 1-wire interface to use the /dev/ttyS0 serial
    port.
    """
    #print 'ow.__init__'
    global initialized
    if not initialized:
        if not _OW.init( iface ):
            raise exNoController
        initialized = True


def finish( ):
    """
    Cleanup the OWFS library, freeing any used resources.
    """
    #print 'Controller.__del__'
    global initialized
    if initialized:
        _OW.finish( )
        initialized = False


#
# 1-wire sensors
#

class Sensor( object ):
    """
    A Sensor is the basic component of a 1-wire network. It represents
    a individual 1-wire element as it exists on the network.
    """
    def __init__( self, path ):
        """
        Create a new Sensor as it exists at the specified path.
        """
        #print 'Sensor.__init__: <%s>' % path
        if not initialized:
            raise exNotInitialized

        self._attrs = { }
        if path == '/':
            self._path    = path
            self._useCache = True
        elif path == '/uncached':
            self._path    = '/'
            self._useCache = False
        else:
            if path[ :len( '/uncached' ) ] == '/uncached':
                self._path     = path[ len( '/uncached' ): ]
                self._useCache = False
            else:
                self._path     = path
                self._useCache = True

        self.useCache( self._useCache )


    def __str__( self ):
        """
        Print a string representation of the Sensor in the form of:

        path - type

        / - DS9490
        """
        #print 'Sensor.__str__'
        return "%s - %s" % ( self._usePath, self._type )


    def __repr__( self ):
        """
        Print a representation of the Sensor in the form of:

        Sensor( path )

        Sensor( / )
        """
        #print 'Sensor.__repr__'
        return 'Sensor("%s")' % self._usePath


    def __eq__( self, other ):
        """
        Two sensors are considered equal if their paths are
        equal. This is done by comparing their _path attributes so
        that cached and uncached Sensors compare equal.

        >>> Sensor( '/' ) == Sensor( '/uncached' )
        True
        """
        return self._path == other._path


    def __getattr__( self, name ):
        """
        Retreive an attribute from the sensor. __getattr__ is called
        only if the named item doesn't exist in the Sensor's
        namespace. If it's not in the namespace, look for the attribute
        on the physical sensor.

        Usage:

            s = ow.Sensor( '/1F.5D0B01000000' )
            print s.family, s.PIO_0

        will result in the family and PIO.0 values being read from the
        sensor and printed. In this example, the family would be 1F
        and thr PIO.0 might be 1.
        """
        #print 'Sensor.__getattr__', name
        if name in self._attrs:
            attr = owfs_get( self._attrs[ name ] )
        else:
            raise AttributeError, name

        return attr


    def __setattr__( self, name, value ):
        """
        Set the value of a sensor attribute. This is accomplished by
        first determining if the physical sensor has the named
        attribute. If it does, then the value is written to the
        name. Otherwise, the Sensor's dictionary is updated with the
        name and value.

        Usage:

            s = ow.Sensor( '/1F.5D0B01000000' )
            s.PIO_1 = '1'

        will set the value of PIO.1 to 1.
        """
        #print 'Sensor.__setattr__', name, value

        # Life can get tricky when using __setattr__. Self doesn't
        # have an _attrs atribute when it's initially created. _attrs
        # is only there after it's been set in __init__. So we can
        # only reference it if it's already been added.
        if hasattr( self, '_attrs' ):
            if name in self._attrs:
                #print 'owfs_put', self._attrs[ name ], value
                owfs_put( self._attrs[ name ], value )
            else:
                self.__dict__[ name ] = value
        else:
            self.__dict__[ name ] = value


    def useCache( self, use_cache ):
        """
        Set the sensor to use the underlying owfs cache (or not)
        depending on the use_cache parameter.

        Usage:

            s = ow.Sensor( '/1F.5D0B01000000' )
            s.useCache( False )

        will set the internal sensor path to /uncached/1F.5D0B01000000.

        Also:

            s = ow.Sensor( '/uncached/1F.5D0B01000000' )
            s.useCache( True )

        will set the internal sensor path to /1F.5D0B01000000.
        """
        self._useCache = use_cache
        if self._useCache:
            self._usePath = self._path
        else:
            if self._path == '/':
                self._usePath = '/uncached'
            else:
                self._usePath = '/uncached' + self._path

        if self._path == '/':
            self._type    = owfs_get( '/system/adapter/name' )
        else:
            self._type  = owfs_get( '%s/type' % self._usePath )
        self._attrs = dict( [ (n.replace( '.', '_' ), self._usePath + '/' + n )
                              for n in owfs_get( self._usePath ).split( ',' ) ] )


    def entries( self ):
        """
        Generator which yields the attributes of a sensor.
        """
        #print 'Sensor.entries'
        list = owfs_get( self._usePath )
        if list:
            for entry in list.split( ',' ):
                if not owfs_get( entry + 'type' ):
                    yield entry.split( '/' )[ 0 ]


    def entryList( self ):
        """
        List of the sensor's attributes.
        """
        #print 'Sensor.entryList'
        return [ e for e in self.entries( ) ]


    def sensors( self, names = [ 'main', 'aux' ] ):
        """
        Generator which yields all the sensors that are associated
        with the current sensor.

        In the event that the current sensor is the adapter (such as a
        DS9490 USB adapter) the list of sensors directly attached to
        the 1-wire network will be yielded.

        In the event that the current sensor is a microlan controller
        (such as a DS2409) the list of directories found in the names
        list parameter will be searched and any sensors found will be
        yielded. The names parameter defaults to [ 'main', 'aux' ].
        """
        #print 'Sensor.sensors'
        if self._type == 'DS2409':
            for branch in names:
                path = self._usePath + '/' + branch
                list = owfs_get( path )
                if list:
                    for branch_entry in list.split( ',' ):
                        branch_path = self._usePath + '/' + branch + '/' + branch_entry.split( '/' )[ 0 ]
                        if owfs_get( branch_path + '/type' ):
                            yield Sensor( branch_path )

        else:
            list = owfs_get( self._usePath )
            if list:
                for branch_entry in list.split( ',' ):
                    if owfs_get( branch_entry + 'type' ):
                        path = self._usePath + '/' + branch_entry.split( '/' )[ 0 ]
                        if path[ :2 ] == '//':
                            path = path[ 1: ]
                        yield Sensor( path )


    def sensorList( self, names = [ 'main', 'aux' ] ):
        """
        List of all the sensors that are associated with the current
        sensor.

        In the event that the current sensor is the adapter (such as a
        DS9490 USB adapter) the list of sensors directly attached to
        the 1-wire network will be yielded.

        In the event that the current sensor is a microlan controller
        (such as a DS2409) the list of directories found in the names
        list parameter will be searched and any sensors found will be
        yielded. The names parameter defaults to [ 'main', 'aux' ].
        """
        #print 'Sensor.sensorList'
        return [ s for s in self.sensors( ) ]


    def find( self, **keywords ):
        """
        Generator which yields all the sensors whose attributes match
        those past in. By default, any matched attribute will yield a
        sensor. If the parameter all is passed to the find call, then
        all the supplied attributes must match to yield a sensor.

        Usage:

            for s in Sensor( '/' ).find( type = 'DS2408' ):
                print s

        will print all the sensors whose type is DS2408.

            root = Sensor( '/' )
            print len( [ s for s in root.find( all = True,
                                               family = '1F',
                                               type = 'DS2409' ) ] )

        will print the count of sensors whose family is 1F and whose
        type is DS2409.
        """
        #print 'Sensor.find', keywords
        #recursion = keywords.pop( 'recursion', False )
        all       = keywords.pop( 'all',       False )

        for sensor in self.sensors( ):
            match = 0
            for attribute in keywords:
                if hasattr( sensor, attribute ):
                    if keywords[ attribute ]:
                        if getattr( sensor, attribute ) == keywords[ attribute ]:
                            match = match + 1
                    else:
                        if hasattr( sensor, attribute ):
                            match = match + 1

            if not all and match:
                yield sensor
            elif all and match == len( keywords ):
                yield sensor
