#!/usr/bin/python
# -*- coding: utf-8 -*-
"""CANopen Object Dictionary

Example
-------
Create an empty Object Dictionary (OD):

>>> import logging, coloredlogs, verboselogs
>>> from extend_logging import extend_logging
>>> from objectDictionary import objectDictionary
>>> logger = logging.getLogger(name='OD')
>>> coloredlogs.install(level='DEBUG', isatty=True)
>>> od = objectDictionary(logger)

In order to create an |OD| from an Electronic Data Sheet (EDS) replace the
last line with:

>>> od = objectDictionary.from_eds(logger, '/path/to/eds', 42)


:Author: Sebastian Scholz
:Contact: sebastian.scholz@cern.ch
:Organization: Bergische Universität Wuppertal
"""
# Standard library modules
import logging
import re
try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import RawConfigParser as ConfigParser

# External dependencies
import coloredlogs as cl
import verboselogs

# Other files
from controlServer.CANopenConstants import ATTR, VARTYPE, ENTRYTYPE, LIMITS
#from extend_logging import extend_logging


def ifNone(a, b):
    """Returns `b` if a is :data:`None` and `a` otherwise"""
    return b if a is None else a


class odEntry():
    """Object dictionary entry

    This class represents a top level entry of an object dictionary. Its value
    may be modified if it defined as writable.

    Parameters
    ----------
    index : :obj:`int`
        The index the |OD| entry shall be initialized with.
    entrytype  : :class:`~.CANopenConstants.ENTRYTYPE`
        Object type of this |OD| entry.
    logger : :obj:`logging.Logger`
        A Logger object for logging purposes
    datatype : :obj:`~.CANopenConstants.VARTYPE`, optional
        Data type if entry is single value entry (Defaults to :data:`None`)
    attribute : :obj:`~.CANopenConstants.ATTR`, optional
        Access attribute if entry is single value entry (Defaults to
        :data:`None`)
    description : :obj:`str`, optional
        Name of the |OD| entry (Defaults to ``''``)
    default: optional
        Default value if entry is single value entry (Defaults to
        :data:`None`)
    comment : :obj:`str`, optional
        Additional comment (Defaults to ``''``)
    direct_access : :obj:`bool`
        True makes it possible to write on all entries
    minimum : :obj:`int`, optional
        Low Limit of this entry.
    maximum : :obj:`int`, optional
        High Limit of this entry.

    Attributes
    ----------
    description : :obj:`str`
        Name of this |OD| entry
    logger : :obj:`logging.Logger`
        A Logger object for logging purposes
    comment : :obj:`str`
        Additional comment describing this entry
    """

    def __init__(self, index, entrytype, logger, datatype=None, attribute=None,
                 description='', default=None, comment='',
                 direct_access=False, minimum=None, maximum=None):
        self.__index = index
        self.description = description
        self.logger = logger
        self.__entrytype = entrytype
        self.__direct_access = direct_access
        self.__minimum, self.__maximum = LIMITS(datatype, minimum, maximum)
        if entrytype is not ENTRYTYPE.VAR:
            self.__attribute = None
            self.__default = None
            self.__subentries = []
            self.__datatype = None            
        else:
            self.__attribute = attribute
            self.__default = default
            self.__subentries = None
            self.__datatype = datatype
        self.__val = self.__default
        self.comment = comment
        self.logger.spam('Created ' + str(self))

    def __str__(self):
        """Create a string containing the index and object type"""
        return 'OD entry at index {:04X}'.format(self.__index) + \
               ' of type ' + self.__entrytype.name

    def __repr__(self):
        """Create a string with python syntax"""
        return 'odEntry(index=0x{:04X}, entrytype=' + str(self.__entrytype) + \
               ')'

    def __len__(self):
        """Length of entry

        Returns
        -------
        :obj:`int`
            The number of subentries
        """
        if self.__subentries is None:
            return 0
        return len(self.__subentries)

    def __getitem__(self, key):
        """Get a subentry

        Parameters
        ----------
        key : :obj:`int`
            index of the subentry

        Returns
        -------
        subentry : :obj:`odSubEntry`
            The subentry
        """
        if self.__entrytype is ENTRYTYPE.VAR and key == 0:
            return self
        if isinstance(key, slice):
            return self.__subentries[key.start:key.stop:key.step]
        if self.__subentries[key].reserved:
            raise IndexError(f'Subentry {key} does not exist or is reserved.')
        return self.__subentries[key]

    def __setitem__(self, key, val):
        """Try to write the value of a subentry

        Parameters
        ----------
        key : :obj:`int`
            Index of the subentry
        val
            Value to write
        """
        self.__subentries[key].value = val

    def __contains__(self, subindex):
        """Checks if this entry has a certain subentry

        Parameters
        ----------
        subindex : :obj:`int`
            The subindex to look for
        """
        if self.__entrytype is ENTRYTYPE.VAR:
            return subindex == 0
        else:
            return subindex < len(self.__subentries)

    @property
    def index(self):
        """:obj:`int` : |OD| main index"""
        return self.__index

    @property
    def entrytype(self):
        """:obj:`~.CANopenConstants.ENTRYTYPE` : Object definition of |OD|
        entry"""
        return self.__entrytype

    @property
    def datatype(self):
        """:class:`.CANopenConstants.VARTYPE` or :data:`None` : Data type
        of |OD| entry"""
        return self.__datatype

    @property
    def attribute(self):
        """:class:`.CANopenConstants.ATTR` : Access attribute to data object"""
        return self.__attribute

    @property
    def default(self):
        """Default value of |OD| entry"""
        return self.__default

    @property
    def subentries(self):
        """:obj:`list` of :obj:`odSubEntry` : List of subentries belonging to
        this :obj:`odEntry`"""
        return self.__subentries
    
    @property
    def minimum(self):
        """:obj:`int` : Low Limit of this entry. -:data:`~math.inf` if not
        specified or :data:`None` if the entry has subideces."""
        return self.__minimum
    
    @property
    def maximum(self):
        """:obj:`int` : High Limit of this entry. :data:`~math.inf` if not
        specified or :data:`None` if the entry has subindeces."""
        return self.__maximum

    @property
    def value(self):
        """Value of |OD| entry"""
        if self.__attribute is ATTR.WO:
            estr = 'OD entry {:04x} is WO'.format(self.index)
            raise AttributeError(estr)
        return self.__val

    @value.setter
    def value(self, val):
        if self.__attribute in [ATTR.WO, ATTR.RW] or self.__direct_access:
            self.__value = val
        else:
            raise AttributeError('Entry may not be written!')

    def addSubEntry(self, subindex, vartype, attribute, description='',
                    default=None, comment='', minimum=None, maximum=None):
        """Add a sub entry to the current |OD| top level entry

        Parameters
        ----------
        subindex : :obj:`int`
            Subindex to be added. Subindeces must be continuous.
        vartype : :obj:`~.CANopenConstants.VARTYPE`
            Data type of future subentry
        attribute : :obj:`~.CANopenConstants.ATTR`
            Access attribute
        description : :obj:`str`, optional
            Name of subentry. Defaults to ``''``.
        default : optional
            Default value. Defaults to :data:`None`.
        comment : :obj:`str`, optional
            Additional comment on subentry. Defaults to ``''``.
        minimum : :obj:`int`, optional
            Low Limit of this entry.
        maximum : :obj:`int`, optional
            High Limit of this entry.

        Raises
        ------
        :exc:`AttributeError`
            If top level entry is of type
            :obj:`.CANopenConstants.ENTRYTYPE.VAR`
        :exc:`ValueError`
            If subindex is not continuous with previous subindeces
        """

        if self.__entrytype is ENTRYTYPE.VAR:
            estr = 'OD Entry {:04x} is of type VAR!'.format(self.__index)
            raise AttributeError(estr)
        while subindex > len(self.__subentries):
            odSE = odSubEntry(master=self, subindex=len(self.__subentries),
                              logger=self.logger, description='reserved',
                              reserved=True, minimum=minimum, maximum=maximum,
                              direct_access=self.__direct_access)
            self.__subentries.append(odSE)
        odSE = odSubEntry(master=self, subindex=subindex, vartype=vartype,
                          attribute=attribute, logger=self.logger,
                          description=description, default=default,
                          comment=comment, direct_access=self.__direct_access,
                          minimum=minimum, maximum=maximum)
        self.__subentries.append(odSE)

    def __iter__(self):
        """Loop over all subentries"""
        return iter(self.__subentries)


class odSubEntry():
    """Low level object dictionary entry

    Parameters
    ----------
    master : :class:`odEntry`
        Top level entry for this subentry. This is needed because this entry
        has to know its main index.
    subindex : :obj:`int`
        Subindex to be initialized with
    vartype : :obj:`~.CANopenConstants.VARTYPE`
        Data type of this entry.
    attribute : :obj:`~.CANopenConstants.ATTR`
        Access attribute for this entry
    logger : :obj:`logging.Logger`
        A Logger object for logging purposes
    description : :obj:`str`, optional
        Name of this entry. Defaults to ``''``.
    default
        Default value of this entry. Defaults to :data:`None`.
    comment : :obj:`str`, optional
        Additional comment for this entry. Defaults to ``''``.
    reserved : :obj:`bool`, optional
        Mark an subentry as reserved for further use.
    direct_access : :obj:`bool`
        True makes it possible to write on all entries.
    minimum : :obj:`int`, optional
        Low Limit of this entry.
    maximum : :obj:`int`, optional
        High Limit of this entry.
    """

    def __init__(self, master, subindex, logger, vartype=None, attribute=None,
                 description='', default=None, comment='', reserved=False,
                 direct_access=False, minimum=None, maximum=None):
        if not reserved:
            if vartype is None:
                raise ValueError(f'Missing VARTYPE for subentry at '
                                 f'{master.index:04X}:{subindex:X}.')
            if attribute is None:
                raise ValueError(f'Missing access attribute for subentry at '
                                 f'{master.index:04X}:{subindex:X}.')
        self.__reserved = reserved
        self.__direct_access = direct_access
        self.__master = master
        self.__subindex = subindex
        self.__vartype = vartype
        self.__attribute = attribute
        self.description = description
        self.comment = comment
        self.logger = logger
        self.__default = default
        self.__minimum, self.__maximum = LIMITS(vartype, minimum, maximum)
        self.__value = default
        self.logger.spam('Created ' + str(self))

    @property
    def reserved(self):
        """:obj:`bool` : If this is a reserved subentry"""
        return self.__reserved

    @property
    def index(self):
        """:obj:`int` : Top level index of this entry"""
        return self.__master.index

    @property
    def subindex(self):
        """:obj:`int` : Low level index of this entry"""
        return self.__subindex

    @property
    def vartype(self):
        """:class:`~.CANopenConstants.VARTYPE` : Data type of this entry"""
        return self.__vartype

    @property
    def attribute(self):
        """:class:`~.CANopenConstants.ATTR` : Access attribute for this
        entry"""
        return self.__attribute

    @property
    def default(self):
        """Default value of this entry"""
        return self.__default

    @property
    def minimum(self):
        """:obj:`int` : Low Limit of this entry. -:data:`~math.inf` if not
        specified."""
        return self.__minimum
    
    @property
    def maximum(self):
        """:obj:`int` : High Limit of this entry. -:data:`~math.inf` if not
        specified."""
        return self.__maximum

    @property
    def value(self):
        """Data value of entry"""
        if self.__attribute is ATTR.WO:
            estr = f'OD entry {self.index:04X}:{self.subindex:X} is WO'
            raise AttributeError(estr)
        elif self.__reserved:
            raise AttributeError(f'OD entry {self.index:04X}:{self.subindex:X}'
                                 ' is reserved.')
        return self.__value

    @value.setter
    def value(self, val):
        if self.__attribute in [ATTR.WO, ATTR.RW] or self.__direct_access:
            self.__value = val
        else:
            raise AttributeError('Entry may not be written!')

    def __str__(self):
        """String containing index, subindex, data type and value"""
        if self.__reserved:
            return f'OD entry at index {self.index:04X}:{self.subindex:X}' +\
                   ' is reserved.'
        return f'OD entry at index {self.index:04X}:{self.subindex:X} of ' + \
               f'type {self.__vartype.name} with data: {self.__value}.'

    def __repr__(self):
        """String containing index, subindex and data type"""
        return f'odSubEntry(index={self.index:04X}, subindex=' + \
               f'{self.subindex:X}, vartype=' + str(self.vartype) + ')'



class objectDictionary():
    """Class which represents an object dictionary and manages its entries

    Parameters
    ----------
    logger : :obj:`logging.Logger`
        A Logger object for logging purposes
    direct_access : :obj:`bool`, optional
        True makes it possible to write on all entries
    """

    def __init__(self, logger, direct_access=False):
        self.logger = logger
        """:obj:`~logging.Logger` : Main logger of this |OD|"""
        self.__direct_access = direct_access
        self.__entries = [None for i in range(0x10000)]
        self.__indices = []
        logger.debug('Created empty object dictionary.')

    @classmethod
    def from_eds(cls, logger, source, node_id, direct_access=False):
        """Import an existing object dictionary form an |EDS| file

        It may happen that not all features of the |EDS| format ar supported by
        this method. In this case the logger displays an ERROR message.

        Parameters
        ----------
        logger : :obj:`logging.Logger`
            A Logger object for logging purposes
        source : :term:`file<file object>` or :obj:`str`
            A file-like object or the path to the eds file
        node_id : :obj:`int`
            The node-id to which this object dictionary shall belong
        direct_access : :obj:`bool`, optional
            True makes it possible to write on all entries
        """
        logger.debug('Importing object dictionary from EDS ...')
        eds = ConfigParser()
        if hasattr(source, "read"):
            fp = source
        else:
            fp = open(source)
        eds.read_file(fp)
        fp.close()
        od = cls(logger, direct_access)
        if eds.has_section("DeviceComissioning"):
            od.bitrate = int(eds.get("DeviceComissioning", "Baudrate")) * 1000
            od.node_id = int(eds.get("DeviceComissioning", "NodeID"))

        for section in eds.sections():
            # Match indexes
            match = re.match(r"^[0-9A-Fa-f]{4}$", section)
            if match is not None:
                index = int(section, 16)
                name = eds.get(section, "ParameterName")
                object_type = ENTRYTYPE(int(eds.get(section, "ObjectType"), 0))

                if object_type == ENTRYTYPE.VAR:
                    minimum, maximum = None, None
                    datatype = VARTYPE(int(eds.get(section, "DataType"), 0))
                    if eds.has_option(section, "LowLimit"):
                        minimum = int(eds[section]["lowLimit"], 0)
                    if eds.has_option(section, "HighLimit"):
                        maximum = int(eds[section]["HighLimit"], 0)
                    if eds.has_option(section, "DefaultValue"):
                        val = cls.parse_value(eds.get(section, "DefaultValue"),
                                              datatype, node_id)
                    else:
                        val = None
                    od.addEntry(index, object_type,
                                datatype=datatype,
                                attribute=ATTR[eds.get(section, "AccessType")],
                                description=name,
                                default=val,
                                minimum=minimum, maximum=maximum)
                elif object_type == ENTRYTYPE.ARRAY and \
                        eds.has_option(section, "CompactSubObj"):
                    od.addEntry(index, object_type, description=name)
                    od[index].addSubEntry(0, VARTYPE.UNSIGNED8, ATTR.RO,
                                          description='Number of entries',
                                          default=0)
                    logger.error('Function \"CompactSubObj\" not yet '
                                 'implemented')
                else:
                    od.addEntry(index, object_type, description=name)

                continue

            # Match subindexes
            match = re.match(r"^([0-9A-Fa-f]{4})sub([0-9A-Fa-f]+)$", section)
            if match is not None:
                index = int(match.group(1), 16)
                subindex = int(match.group(2), 16)
                name = eds.get(section, "ParameterName")
                default = None
                datatype = VARTYPE(int(eds.get(section, "DataType"), 0))
                minimum, maximum = None, None
                if eds.has_option(section, "DefaultValue"):
                    default = cls.parse_value(eds.get(section, "DefaultValue"),
                                              datatype, node_id)
                if eds.has_option(section, "LowLimit"):
                    minimum = int(eds[section]["lowLimit"], 0)
                if eds.has_option(section, "HighLimit"):
                    maximum = int(eds[section]["HighLimit"], 0)
                if od[index].entrytype != ENTRYTYPE.VAR:
                    od[index].addSubEntry(subindex, datatype,
                                          ATTR[eds.get(section, "AccessType")],
                                          description=name, default=default,
                                          minimum=minimum, maximum=maximum)
                else:
                    logger.error('Top level entry is VAR and may not have any '
                                 'subentries!')

        od.logger.success('Successfully created OD from EDS.')
        return od

    def parse_value(val_as_string, datatype, node_id):
        """Parse a value from an |EDS| file

        Parameters
        ----------
        val_as_string : :obj:`str`
            The value gotten from the config parser
        datatype : :obj:`~.CANopenConstants.ATTR`
            Datatype of the entry

        Returns
        -------
        value : :obj:`int` or :obj:`str`
            The value in an appropiate type
        """
        if datatype.value == 1:
            val = bool(int(val_as_string))
        elif datatype in [VARTYPE.VISISBLE_STRING, VARTYPE.OCTET_STRING]:
            val = val_as_string
        elif datatype in [VARTYPE.REAL32, VARTYPE.REAL64]:
            val = float(val_as_string)
        else:
            if '$NODEID' in val_as_string:
                val = node_id + int(val_as_string.split('+')[1], 0)
            else:
                val = int(val_as_string, 0)
        return val

    @property
    def indices(self):
        """:obj:`list` : All currently used indices in this |OD|"""
        return self.__indices

    @property
    def entries(self):
        """:obj:`list` : List of entries where not defined entries are
        :data:`None`."""
        return self.__entries

    @property
    def direct_access(self):
        """:obj:`bool`: True makes it possible to write on all entries"""
        return self.__direct_access

    def __getitem__(self, key):
        """Adress an entry via its index

        Parameters
        ----------
        index : :obj:`int`
            Index of |OD| entry

        Returns
        -------
        :obj:`odEntry`
            |OD| entry with specified index

        Raises
        ------
        :exc:`IndexError`
            If index is not part of object dictionary
        """

        if isinstance(key, slice):
            if not all([i in self.indices for i in
                        range(ifNone(key.start, 0), key.stop,
                              ifNone(key.step, 1))]):
                raise IndexError('Not all indices in the given range are in '
                                 'the OD.')
            return self.__entries[key.start:key.stop:key.step]
        if key not in self.indices:
            estr = f'Index {key:04X} not in object dictionary.'
            raise IndexError(estr)
        return self.__entries[key]

    def __setitem__(self, index, val):
        """Try to set the value of an entry

        Parameters
        ----------
        index : :obj:`int`
            Index of the entry
        val
            Value to be written

        Raises
        ------
        :exc:`IndexError`
            If index is not part of object dictionary
        """
        if index not in self.__indices:
            estr = f'Index {index:04X} not in object dictionary.'
            raise IndexError(estr)
        self.__entries[index].value = val

    def addEntry(self, index, entrytype, datatype=None, attribute=None,
                 description='', default=None, comment='', minimum=None, 
                 maximum=None):
        """Add an odEntry to the object dictionary if index is still free

        Parameters
        ----------
        index : :obj:`int`
            The index of the odEntry to be added
        entrytype : :obj:`~.CANopenConstants.ENTRYTYPE`
            Object type of the object to be added.
        datatype : :obj:`~.CANopenConstants.VARTYPE`, optional
            Data type if single value entry.
        attribute : :obj:`~.CANopenConstants.ATTR`, optional
            Access attribute if single value entry.
        description : :obj:`str`, optional
            Name of the entry to be added. Defaults to ``''``.
        default
            Default value if single value entry. Defaults to :data:`None`.
        comment : :obj:`str`, optional
            Additional comment on this entry. Defaults to ``''``.
        minimum : :obj:`int`, optional
            Low Limit of this entry.
        maximum : :obj:`int`, optional
            High Limit of this entry.

        Raises
        ------
        :exc:`IndexError`
            If index is already defined
        """

        if index in self.__indices:
            estr = f'Index {index:04X} already in object dictionary.'
            raise IndexError(estr)
        self.__indices.append(index)
        self.__indices.sort()
        self.__entries[index] = odEntry(index=index, entrytype=entrytype,
                                        logger=self.logger,
                                        datatype=datatype, attribute=attribute,
                                        description=description,
                                        default=default, comment=comment,
                                        direct_access=self.__direct_access,
                                        minimum=minimum, maximum=maximum)

    def __len__(self):
        """Number of all defined top level entries"""
        return len(self.__indices)

    def __iter__(self):
        """Create an iterator to loop over all entries"""
        self.__i = 0
        return self

    def __next__(self):
        """Loop over defined indices

        Returns
        -------
        :obj:`odEntry`
            |OD| entry at this index

        Raises
        ------
        :exc:`StopIteration`
            If there are no more defined indices left
        """
        if self.__i >= len(self.__indices):
            raise StopIteration
        ret = self.__entries[self.__indices[self.__i]]
        self.__i += 1
        return ret

    def __contains__(self, index):
        """Check if index exists in object dictionary

        Parameters
        ----------
        index : :obj:`int`
            Index of |OD| entry
        """
        return index in self.__indices


if __name__ == '__main__':
    extend_logging()
    verboselogs.install()
    logger = logging.getLogger(name='OD')
    logformat = '%(asctime)s %(name)s[%(process)d] %(levelname)-8s ' + \
                '%(message)s'
    cl.install(fmt=logformat, level=logging.DEBUG, isatty=True)

    fp = 'CANControllerForPSPPv1.eds'
    od = objectDictionary.from_eds(logger, fp, 42)
    try:
        od[0x2200][2].value = True
    except AttributeError as ex:
        logger.exception(ex)
