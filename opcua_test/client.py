from opcua import Client
import time
url ="opc.tcp://localhost:4840/"
client=Client(url)
client.connect()
print("Client connected")

while True:
    Temp = client.get_node("ns=2;i=2")
    Temprature =Temp.get_value()
    print("Temperature:",Temprature)
    
    Press = client.get_node("ns=2;i=3")
    Pressure =Press.get_value()
    print("Pressure:",Pressure)
    
    TIME = client.get_node("ns=2;i=4")
    TIME_Value =TIME.get_value()
    print("TIME:",TIME_Value)
    
    time.sleep(1)