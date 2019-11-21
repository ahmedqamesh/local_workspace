from opcua import Client
import time
#from dcsControllerServer.dcsControllerServer import DCSControllerServer
#with DCSControllerServer(interface='AnaGate') as Client:
#    Client.getConnectedPSPPs()
    
url ="opc.tcp://localhost:4840/"
client=Client(url)
client.connect()
print("Client connected")

while True:
    #get_ADCTRIM = client.get_node("ns=2;i=8476")
    #ADCTRIM = get_ADCTRIM.get_value()
    #print("ADCTRIM:",ADCTRIM)
    #get_NodeID = client.get_node("ns=2;i=8530")
    #print(get_NodeID)
    #NodeID =get_NodeID.get_value()
    #print("NodeID:",NodeID)
    #get_Status = client.get_node("ns=2;i=10395")
    #Status = get_Status.get_value()
    #print ("Status:",Status)
    
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