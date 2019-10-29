from opcua import Server
from random import randint
import datetime
import time
server = Server()
# Server runs on a specific IP address
url ="opc.tcp://localhost:4840"
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

# Make the variables writable
Temp.set_writable()
Press.set_writable()
Time.set_writable()


# Start the server
server.start()
print("Server started at{}".format(url))


# Assign values to the parameters
while True:
    Temperature =randint(10,50)
    Pressure = randint(200,999)
    TIME = datetime.datetime.now()
    
    print(Temperature,Pressure,TIME)
    
    Temp.set_value(Temperature)
    Press.set_value(Pressure)
    Time.set_value(TIME)
    time.sleep(2)
    
    
    
    
    
    
    
    
    
    
    