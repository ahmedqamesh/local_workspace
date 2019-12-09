# -*- coding: utf-8 -*-
"""
Created on Sep 23 14:29:35 2019
@author: Ahmed Qamesh
"""
import analib
import time
from collections import deque, Counter
from threading import Thread, Event, Lock
from canlib import canlib, Frame
import ctypes as ct

class sdoReadCAN(object):
    def __init__(self,ipAddress='192.168.1.254',channel=0,bitrate=125000):
        print("Intializing reading class")
        self.__cnt = Counter()

        self.__ch = analib.Channel(ipAddress, channel, baudrate=bitrate)
        self.__cbFunc = analib.wrapper.dll.CBFUNC(self._anagateCbFunc())
        self.__ch.setCallback(self.__cbFunc)
        
        # Initialize default arguments
        self.__canMsgQueue = deque([], 10)
        self.__lock = Lock()

    @property
    def channel(self):
        """Currently used |CAN| channel. The actual class depends on the used
        |CAN| interface."""
        return self.__ch
            
    @property
    def lock(self):
        """:class:`~threading.Lock` : Lock object for accessing the incoming
        message queue :attr:`canMsgQueue`"""
        return self.__lock
    
    @property
    def cnt(self):
        """:class:`~collections.Counter` : Counter holding information about
        quality of transmitting and receiving. Its contens are logged when the
        program ends."""
        return self.__cnt
    
    @property
    def canMsgQueue(self):
        """:class:`collections.deque` : Queue object holding incoming |CAN|
        messages. This class supports thread-safe adding and removing of
        elements but not thread-safe iterating. Therefore the designated
        :class:`~threading.Lock` object :attr:`lock` should be acquired before
        accessing it.

        The queue is initialized with a maxmimum length of ``1000`` elements
        to avoid memory problems although it is not expected to grow at all.

        This special class is used instead of the :class:`queue.Queue` class
        because it is iterable and fast."""
        return self.__canMsgQueue
            
        
        
    def sdoRead(self, nodeId, index, subindex, timeout=100,MAX_DATABYTES=8):
        """Read an object via |SDO|
    
        Currently expedited and segmented transfer is supported by this method.
        The user has to decide how to decode the data.
    
        Parameters
        ----------
        nodeId : :obj:`int`
            The id from the node to read from
        index : :obj:`int`
            The Object Dictionary index to read from
        subindex : :obj:`int`
            |OD| Subindex. Defaults to zero for single value entries.
        timeout : :obj:`int`, optional
            |SDO| timeout in milliseconds
    
        Returns
        -------
        :obj:`list` of :obj:`int`
            The data if was successfully read
        :data:`None`
            In case of errors
        """
        SDO_TX =0x580  
        SDO_RX = 0x600  
        if nodeId is None or index is None or subindex is None:
            return None
        self.cnt['SDO read total'] += 1
        cobid = SDO_RX + nodeId
        msg = [0 for i in range(MAX_DATABYTES)]
        msg[1], msg[2] = index.to_bytes(2, 'little')
        msg[3] = subindex
        msg[0] = 0x40
        try:
            self.__ch.write(cobid, msg)
        except CanGeneralError:
            self.cnt['SDO read request timeout'] += 1
            return None
        
        # Wait for response
        t0 = time.perf_counter()
        messageValid = False
        while time.perf_counter() - t0 < timeout / 1000:
            with self.__lock:
                for i, (cobid_ret, ret, dlc, flag, t) in \
                        zip(range(len(self.__canMsgQueue)),
                            self.__canMsgQueue):
                    messageValid = \
                        (dlc == 8 and cobid_ret == SDO_TX + nodeId
                         and ret[0] in [0x80, 0x43, 0x47, 0x4b, 0x4f, 0x42] and
                         int.from_bytes([ret[1], ret[2]], 'little') == index
                         and ret[3] == subindex)
                    if messageValid:
                        del self.__canMsgQueue[i]
                        break
            if messageValid:
                break
        else:
            self.cnt['SDO read response timeout'] += 1
            return None
        # Check command byte
        if ret[0] == 0x80:
            abort_code = int.from_bytes(ret[4:], 'little')
            self.cnt['SDO read abort'] += 1
            return None
        nDatabytes = 4 - ((ret[0] >> 2) & 0b11) if ret[0] != 0x42 else 4
        data = []
        for i in range(nDatabytes):
            data.append(ret[4 + i])
        return int.from_bytes(data, 'little')
    
    

    def _anagateCbFunc(self):
        """Wraps the callback function for AnaGate |CAN| interfaces. This is
        neccessary in order to have access to the instance attributes.

        The callback function is called asychronous but the instance attributes
        are accessed in a thread-safe way.

        Returns
        -------
        cbFunc
            Function pointer to the callback function
        """

        def cbFunc(cobid, data, dlc, flag, handle):
            """Callback function.

            Appends incoming messages to the message queue and logs them.

            Parameters
            ----------
            cobid : :obj:`int`
                |CAN| identifier
            data : :class:`~ctypes.c_char` :func:`~cytpes.POINTER`
                |CAN| data - max length 8. Is converted to :obj:`bytes` for
                internal treatment using :func:`~ctypes.string_at` function. It
                is not possible to just use :class:`~ctypes.c_char_p` instead
                because bytes containing zero would be interpreted as end of
                data.
            dlc : :obj:`int`
                Data Length Code
            flag : :obj:`int`
                Message flags
            handle : :obj:`int`
                Internal handle of the AnaGate channel. Just needed for the API
                class to work.
            """
            data = ct.string_at(data, dlc)
            t = time.time()
            with self.__lock:
                self.__canMsgQueue.appendleft((cobid, data, dlc, flag, t))
            self.dumpMessage(cobid, data, dlc, flag)

        return cbFunc
    
    def dumpMessage(self,cobid, msg, dlc, flag):
        """Dumps a CANopen message to the screen and log file
    
        Parameters
        ----------
        cobid : :obj:`int`
            |CAN| identifier
        msg : :obj:`bytes`
            |CAN| data - max length 8
        dlc : :obj:`int`
            Data Length Code
        flag : :obj:`int`
            Flags, a combination of the :const:`canMSG_xxx` and
            :const:`canMSGERR_xxx` values
        """
    
        if (flag & canlib.canMSG_ERROR_FRAME != 0):
            print("***ERROR FRAME RECEIVED***")
        else:
            msgstr = '{:3X} {:d}   '.format(cobid, dlc)
            for i in range(len(msg)):
                msgstr += '{:02x}  '.format(msg[i])
            msgstr += '    ' * (8 - len(msg))




if __name__=='__main__':
    print('Writing example CAN Expedited read message ...')
    sdo = sdoReadCAN()
    NodeId = 8
    #Example (1): get node Id
    VendorId = sdo.sdoRead(NodeId, 0x1000,0,1000)
    print(f'VendorId: {VendorId:03X}')
    
    #Example (2): print Pspp parameters ( 4 PSPPs)
    N_PSPP =4
    for PSPP in range(0,N_PSPP): # Each i represents one PSPP
        index = 0x2200+PSPP
        subindex = 1
        monVals = sdo.sdoRead(NodeId, index,subindex,3000)
        vals = [(monVals >> i * 10) & (2**10 - 1) for i in range(3)]
        print(f'PSPP: {PSPP} ,Temp1: {vals[0]} ,Temp2: {vals[1]} ,Voltage: {vals[2]}')
