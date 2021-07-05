# -*- coding: utf-8 -*-
"""
Created on Mon Jul 23 14:29:35 2018
@author: Sebastian
"""
import analib
import time


if __name__=='__main__':

    # dll = analib.wrapper.dll

    ret = analib.wrapper.dllInfo()
    print(f'DLL version: "{ret}"')

    with analib.channel.Channel(port=1) as ch:
        print(f'State: {ch.state}')

        print('Writing example CAN message ...')
        #ch.write(0x42, [1, 2, 3, 4, 5, 6, 7])
        
        # Define parameters
        NodeId = 1
        SDO_RX = 0x600
        index = 0x1000
        Byte0= cmd = 0x40 
        Byte1, Byte2 = index.to_bytes(2, 'little')
        Byte3 = subindex = 0 
        ch.write(SDO_RX + NodeId, [Byte0,Byte1,Byte2,Byte3,0,0,0,0])
        print('Reading messages ...')        
        
        
        s, m = ch.getTime()
        print(f'Time: {time.ctime(s + m / 1000000)}')
        print('Setting Time ...')
        ch.setTime()
        s, m = ch.getTime()
        print(f'Time: {time.ctime(s + m / 1000000)}')

        # print('Restarting device ...')
        # analib.wrapper.restart(ch.ipAddress)

        print('Reading messages ...')
        while True:
            try:
                cobid, data, dlc, flag, t = ch.getMessage()
                print(f'ID: {cobid:03X}; Data: {data.hex()}, DLC: {dlc}')
            except analib.CanNoMsg:
                pass