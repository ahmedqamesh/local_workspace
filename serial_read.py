import serial;
import io;
import time;
import os;
if __name__ == '__main__' :
# configure the serial connections (the parameters differs on the device you are connecting to)
    i =2
    while True:
        with serial.Serial(port='/dev/ttyUSB'+str(i), 
                           baudrate=9600,#115200,
                           bytesize = serial.EIGHTBITS, 
                           parity = serial.PARITY_NONE,#The parity bit checks errors based on the number of ones transmitted (e.g. even parity (==1) = even No. of ones)
                           stopbits = serial.STOPBITS_ONE,  
                           timeout=1, 
                           xonxoff=True,
                           rtscts=False,# not a virtual port
                           dsrdtr=False,#not a virtual port
                           writeTimeout = 2) as s:
            #s.flush()
            print("Reading ttyUSB"+str(i))
            if s.is_open== False : s.open()
            else:pass
            
            data = s.read()
            data+= s.read(s.inWaiting())  
            binary_string=""
            #binary_string = "{:08b}".format(int(data.hex(),16))
            print(data.hex(),len(data),binary_string)
            #Write the bytes data to the port. 
            #This should be of type bytes (or compatible such as bytearray). 
            #s.write(bytearray('dead','ascii'))
            #s.write(data)
            wdata = bytes(b'E')
            print(wdata.hex())
            s.write(wdata)
            #s.write(b'DEAD')
            #Unicode strings must be encoded 
           # s.write("DEAD".encode('utf-8'))    
            
            print("=================================")
            #time.sleep(0.5)
        #s.close()
    

  
           