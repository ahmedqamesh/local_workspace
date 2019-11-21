 
from opcua import Server
from random import randint
import datetime
import time
server = Server()
# Server runs on a specific IP address
url ="opc.tcp://localhost:4840/"
server.set_endpoint(url)
 
 
# Define address space
name = "OPCUA_SIMULATION_SERVER"
addspace = server.register_namespace(name)
 
#Define root node
node =server.get_objects_node()
 
# Define node to store parameters
param = node.add_object(addspace,"parameters")
 
#Define Variables
Temp = param.add_variable(addspace,"Temperature",0)
Press = param.add_variable(addspace,"Pressure",0)
Time = param.add_variable(addspace,"Time",0)


vMon = param.add_variable(addspace,"vMon",0)
vzero = param.add_variable(addspace,"v0",0)
onOff = param.add_variable(addspace,"onOff",0)
isOn = param.add_variable(addspace,"isOn",0)
 
# Make the variables writable
Temp.set_writable()
Press.set_writable()
Time.set_writable()

vMon.set_writable()
vzero.set_writable()
onOff.set_writable()
isOn.set_writable()

# Start the server
server.start()
print("Server started at{}".format(url))
 
 
# Assign values to the parameters
while True:
    Temperature =randint(10,50)
    Pressure = randint(10,50)
    TIME = datetime.datetime.now()
    
    vMon_value =randint(0,10)
    vzero_value =randint(10,20)
    onOff_value =bool(randint (0,1))
    isOn_value = bool(randint (0,1))
    
    print(Temperature,Pressure,TIME,vMon_value,vzero_value,onOff_value, isOn_value)
    
    Temp.set_value(Temperature)
    Press.set_value(Pressure)
    Time.set_value(TIME)
    
    vMon.set_value(vMon_value)
    vzero.set_value(vzero_value)
    onOff.set_value(onOff_value)
    isOn.set_value(isOn_value)
    time.sleep(2)
