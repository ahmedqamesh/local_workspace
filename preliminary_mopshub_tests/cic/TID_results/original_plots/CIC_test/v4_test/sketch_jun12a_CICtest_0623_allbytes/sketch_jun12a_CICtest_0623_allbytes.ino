// include the SPI library:
#include <SPI.h>
#include <math.h>

// Version 30.6.2022  mod. 13.4.2023
// NEU 12.6.23 für CIC0623 mit 8-Bit-Register für Enable und 3 Bit Voltage-Set (jeweils mit Doppelbit)

             

// set pin 10 as the slave select for the digital pot:
const int CANRXA_Pin = 3;  // receiving CAN data
const int CANRXB_Pin = 4;
const int CANTXA_Pin = 5;   // sending CAN data
const int CANTXB_Pin = 6;
const int MCSA_Pin =  7;    // chip select monitor A = ADC
const int CCSA_Pin =  8;    // chip select control A = power enable register
const int MCSB_Pin =  9;    // chip select monitor B = ADC
const int CCSB_Pin = 10;    // chip select control B = power enable register
// MOSI = Slave DIN = 11    // handled by SPI....-commands
// MISO = Slave DOUT = 12
// SCK  = Master-Clock = 13

byte powerset = 255;

void setup() {



analogReference(INTERNAL);
//type =  (DEFAULT, INTERNAL, INTERNAL1V1, INTERNAL2V56, or EXTERNAL). 


  
  // set the slaveSelectPin as an output:
  pinMode(MCSA_Pin, OUTPUT);
  pinMode(CCSA_Pin, OUTPUT);
  pinMode(MCSB_Pin, OUTPUT);
  pinMode(CCSB_Pin, OUTPUT);

  // initialize SPI:
  SPI.begin();
  SPI.beginTransaction(SPISettings(10000, MSBFIRST, SPI_MODE0));

 // Send "CAN-Signal", approx. 980 Hz, duty cycle 0..100 % = value 0..255
// analogWrite(5, 112); 
//   analogWrite(6, 144); 

  // to do/replace: 
  // send CAN TXA and TXB 
  // using digitalWrite(CANTXA_Pin, HIGH); and (CANTXA_Pin, LOW);
  // check the RXA and RXB 
  // using  digitalRead(CANRXA_Pin); digitalRead(CANRXB_Pin); 

  Serial.begin(9600);
  
}

/*
Description
SPI transfer is based on a simultaneous send and receive: 
the received data is returned in receivedVal 
(or receivedVal16). 
In case of buffer transfers the received data 
is stored in the buffer in-place 
(the old data is replaced with the data received).

Syntax
receivedVal = SPI.transfer(val)
receivedVal16 = SPI.transfer16(val16)
SPI.transfer(buffer, size)

Parameters
val: the byte to send out over the bus
val16: the two bytes variable to send out over the bus
buffer: the array of data to be transferred 
 * 
 *CS: 
 With most SPI devices, after SPI.beginTransaction(), 
 you will write the slave select pin LOW, 
 call SPI.transfer() any number of times to transfer data, 
 then write the SS pin HIGH, 
 and finally call SPI.endTransaction(). 
 * 
 // take the SS pin low to select the chip:
  digitalWrite(slaveSelectPin, LOW);
 * 
 */

// MCP23S17 is the OLDER Type of power enable register
void SET_POWER23S17(int side, int state) {
    int CCS_Pin;
  if (side == 1) CCS_Pin = CCSA_Pin;
  if (side == 2) CCS_Pin = CCSB_Pin;
digitalWrite(CCS_Pin, LOW);
delay(1); // Delay in Millisec
SPI.transfer(0x40);  // slave adress write  MCP23S17
delay(1); 
SPI.transfer(0x00); // reg = IODIRA 
delay(1); 
SPI.transfer(0x00); // set IODIRA , 1 = inputs / 0 = outputs
delay(1); 
digitalWrite(CCS_Pin, HIGH);
 delay(4); 
digitalWrite(CCS_Pin, LOW);
delay(1); // Delay in Millisec
SPI.transfer(0x40);  // slave adress write  MCP23S17
delay(1); 
SPI.transfer(0x12); // GPIOA 
delay(1); 
SPI.transfer(state); // set GPIOA 
delay(1); 
digitalWrite(CCS_Pin, HIGH);
}

// MCP23S08 is the NEW Type of power enable register
void SET_POWER23S08(int side, int state) {
    int CCS_Pin;
  if (side == 1) CCS_Pin = CCSA_Pin;
  if (side == 2) CCS_Pin = CCSB_Pin;
digitalWrite(CCS_Pin, LOW);
delay(1); // Delay in Millisec
SPI.transfer(0x40);  // slave adress write  MCP23S17
delay(1); 
SPI.transfer(0x00); // reg = IODIRA 
delay(1); 
SPI.transfer(0x00); // set IODIRA , 1 = inputs / 0 = outputs
delay(1); 
digitalWrite(CCS_Pin, HIGH);
 delay(4); 
digitalWrite(CCS_Pin, LOW);
delay(1); // Delay in Millisec
SPI.transfer(0x40);  // slave adress write  MCP23S17
delay(1); 
SPI.transfer(0x09); // GPIOA 12 bei 23S17, GPIO 09 bei 23S08
delay(1); 
SPI.transfer(state); // set GPIO(A) 
delay(1); 
digitalWrite(CCS_Pin, HIGH);
}

//--------- ADC is CS5525-ARZ, has 4 channels 16 Bit
// already used at CERN, radiation tolerant qualified (ELMB2) 
// readout is a bit complex ...

void ADCRW(int side, int channel) {
// ADC-Init  15 Bytes FF, 1 Byte FE
   int MCS_Pin, channelbyte;
   int i, byte1, byte2, byte3, byte4, byte5, byte6;
   long ADC_value, current_ma;
   float ADC_voltage, R_NTC, temperature;
   if (side == 1) MCS_Pin = MCSA_Pin;
   if (side == 2) MCS_Pin = MCSB_Pin;
 digitalWrite(MCS_Pin, LOW);
    for (i=1; i<16; i++) {
      SPI.transfer(0xff);  
      delay(1); 
      }
    SPI.transfer(0xfe);    
    delay(1); 
// ADC-Reset
   SPI.transfer(0x03);   
   SPI.transfer(0x00);   
   SPI.transfer(0x00);   
   SPI.transfer(0x80);
     delay(1); 
  digitalWrite(MCS_Pin, HIGH);
  delay(1); 
  digitalWrite(MCS_Pin, LOW);
  delay(1); 
   SPI.transfer(0x03);   
   SPI.transfer(0x00);   
   SPI.transfer(0x00);   
   SPI.transfer(0x00);  
  delay(1); 
  digitalWrite(MCS_Pin, HIGH);
  delay(1); 
  digitalWrite(MCS_Pin, LOW);
 byte1 =  SPI.transfer(0x0b);   
 byte2 =  SPI.transfer(0x00);   
 byte3 =  SPI.transfer(0x00);   
 byte4 =  SPI.transfer(0x00);   
//Serial.print(byte4 , HEX);
//Serial.print(" - ");   // sollte 0x40 sein
  digitalWrite(MCS_Pin, HIGH);
  delay(1); 
  digitalWrite(MCS_Pin, LOW);
 byte1 =  SPI.transfer(0x0b);   
 byte2 =  SPI.transfer(0x00);   
 byte3 =  SPI.transfer(0x00);   
 byte4 =  SPI.transfer(0x00);   
//Serial.print(byte4 , HEX);
//Serial.println(" << Reset soll 40 - 0"); // sollte 0x00 sein
  digitalWrite(MCS_Pin, HIGH);
  delay(1); 
  
// ADC-configuration
  digitalWrite(MCS_Pin, LOW);
   SPI.transfer(0x03);   
   SPI.transfer(0x00);   
   SPI.transfer(0x30);   // number of CSRs
   SPI.transfer(0x00);  
  delay(1);   
   digitalWrite(MCS_Pin, HIGH);

 digitalWrite(MCS_Pin, LOW);   // readback for control
   SPI.transfer(0x0b);   
   byte1 = SPI.transfer(0x00);   
   byte2 = SPI.transfer(0x00);
   byte3 = SPI.transfer(0x00);  
  delay(1);   
   digitalWrite(MCS_Pin, HIGH);
//Serial.print(byte1 , HEX); Serial.print("-");
//Serial.print(byte2 , HEX); Serial.print("-");
//Serial.print(byte3 , HEX); 
//Serial.println(" <<  Config read");

  delay(2); 
   digitalWrite(MCS_Pin, LOW);
   SPI.transfer(0x05);   
   SPI.transfer(0x02);   
   SPI.transfer(0xb0);   
   SPI.transfer(0xab);  
   SPI.transfer(0x12);   
   SPI.transfer(0xb1);   
   SPI.transfer(0xab);   //  ab statt a9 für 2,5 V statt 5,0 V range in ch 3
  delay(1);   
   digitalWrite(MCS_Pin, HIGH);
  delay(2); 

 digitalWrite(MCS_Pin, LOW);   // readback for control
           SPI.transfer(0x0d);   
   byte1 = SPI.transfer(0x00);   
   byte2 = SPI.transfer(0x00);
   byte3 = SPI.transfer(0x00);  
   byte4 = SPI.transfer(0x00);   
   byte5 = SPI.transfer(0x00);
   byte6 = SPI.transfer(0x00);  
  delay(1);   
   digitalWrite(MCS_Pin, HIGH);
//Serial.print(byte1 , HEX); Serial.print("-");
//Serial.print(byte2 , HEX); Serial.print("-");
//Serial.print(byte3 , HEX); Serial.print("-");
//Serial.print(byte4 , HEX); Serial.print("-");
//Serial.print(byte5 , HEX); Serial.print("-");
//Serial.print(byte6 , HEX); 
//Serial.println(" <<  CSRs read");

delay(100);   
 
// ADC-calibration

// ADC-channel  // offset cal.
   digitalWrite(MCS_Pin, LOW);
   delay(10);     
   channelbyte = (channel * 8) ;
   channelbyte = channelbyte | 0x81 ;
//Serial.print(channelbyte , HEX); Serial.print(": ");   
          SPI.transfer(channelbyte); 
   digitalWrite(MCS_Pin, HIGH);
   delay(10); 

// ADC-channel  // gain cal.
   digitalWrite(MCS_Pin, LOW);
   delay(10);     
   channelbyte = (channel * 8) ;
   channelbyte = channelbyte | 0x82 ;
//Serial.print(channelbyte , HEX); Serial.print(": ");   
          SPI.transfer(channelbyte); 
   digitalWrite(MCS_Pin, HIGH);
   delay(10); 

  
  
// ADC-channel-read
   digitalWrite(MCS_Pin, LOW);
   delay(10);     
   channelbyte = (channel * 8) ;
   channelbyte = channelbyte | 0x80 ;
//Serial.print(channelbyte , HEX); Serial.print(": ");   
          SPI.transfer(channelbyte); 
 byte1 =  SPI.transfer(0x00);  
 byte2 =  SPI.transfer(0x00);   
 byte3 =  SPI.transfer(0x00);   
 byte4 =  SPI.transfer(0x00);   
//Serial.print(byte1 , HEX); Serial.print("-");
//Serial.print(byte2 , HEX); Serial.print("-");
//Serial.print(byte3 , HEX); Serial.print("-");
//Serial.print(byte4 , HEX);

//Serial.println(" << read ch (lastbyte)"); 
 delay(1);   
   digitalWrite(MCS_Pin, HIGH);
 delay(100);   

   digitalWrite(MCS_Pin, LOW);
          SPI.transfer(channelbyte);   
 byte1 =  SPI.transfer(0x00);  
 byte2 =  SPI.transfer(0x00);   
 byte3 =  SPI.transfer(0x00);   
 byte4 =  SPI.transfer(0x00);   
   if (side == 1) Serial.print(" A");
   if (side == 2) Serial.print(" B");
 Serial.print(channel); Serial.print(" ADC: ");   
//Serial.print(byte1 , HEX); Serial.print("-");
//Serial.print(byte2 , HEX); Serial.print("-");
//Serial.print(byte3 , HEX); Serial.print("-");
//Serial.print(byte4 , HEX);
Serial.print( " = value dec ");
ADC_value = (256L * byte2) + byte3;
Serial.print(ADC_value, DEC);
ADC_voltage = ADC_value ; 
ADC_voltage = ADC_voltage / 65535 ; 
ADC_voltage = ADC_voltage * 2.5 ;
// ch0 .. ch2 are via voltage divider 1/2, so multiply by 2
if (channel <3){  
  ADC_voltage = ADC_voltage * 2 ;   
  }
Serial.print( " = mV ");
Serial.print(ADC_voltage * 1000, 2);
if (channel == 1) {
  current_ma = 1000 * ADC_voltage;
Serial.print( " = current/mA  ");
Serial.print(current_ma, DEC);  
  }

if (channel == 3) {   // NTC voltage  to temperature
R_NTC = 10000.0 / ( (2.5 / ADC_voltage) - 1 );
Serial.println(" > "); 
Serial.print(" R-NTC (Ohm) "); 
Serial.print(R_NTC); 

temperature = (1/((   ( log(R_NTC/10000) / 3435) ) + (1/298.15) ))-273.15;
Serial.print("  >>   T(C): "); 
Serial.println(temperature,2);  

/*
temperature =  log (R_NTC)   ;
Serial.print("log R "); 
Serial.println(temperature,8);   

temperature =  temperature - 9.2103;  // - ln 10000.0   ;
Serial.print(" ln(R/10k) "); 
Serial.println(temperature,8);   

temperature = temperature/3435   ;
Serial.print(" ln/3435 "); 
Serial.println(temperature,8);   

temperature = temperature + (1/298.15);
Serial.print(" ln/3435 + 1/T0 "); 
Serial.println(temperature,8);   

temperature = 1 / temperature ;
Serial.print(" 1/ ...  = K "); 
Serial.println(temperature,8);   

temperature = temperature -273.15  ;
Serial.print(" NTC-Temp (C) "); 
Serial.println(temperature);   
*/
}
  
//Serial.println(" << "); 
 delay(1);   
   digitalWrite(MCS_Pin, HIGH);
 delay(1);   


 }

// %%%%%%%%%%%%%%%%%%%% MAIN LOOP  %%%%%%%%%%%%%%%%%%%%%%%%%%

void loop() {
  
  word Ard_ADC0,Ard_ADC1,Ard_ADC2,Ard_ADC3,Ard_ADC4,Ard_ADC5;
 float fArd_ADC0,fArd_ADC1,fArd_ADC2,fArd_ADC3,fArd_ADC4,fArd_ADC5;
 byte inbyte;
 
  // put your main code here, to run repeatedly:

            // send data only when you receive data:
        if (Serial.available() > 0) {
                // read the incoming byte:
                inbyte = Serial.read();

                // say what you got:
                Serial.print("received deci: ");
                Serial.print(inbyte, DEC);
                Serial.print(" = hex : ");
                Serial.print(inbyte, HEX);
                Serial.print(" = bin : ");
                Serial.println(inbyte, BIN);   

                           powerset = inbyte;
        }


/////////
powerset = powerset +1 ;

//----------- POWER ON ---------------
//byte powerset in setup auf 255 default

SET_POWER23S08(2,powerset);  // 23S17 alt
delay(10); 
SET_POWER23S08(1,powerset);  
delay(100);   

 Serial.println("  ====ON== "); 
Serial.print(" ON ="); 
//  Serial.print(powerset, DEC);
  Serial.print(" = hex : ");
  Serial.print(powerset, HEX);
  Serial.print(" # ");
//  Serial.println(powerset, BIN);  



// -------- read and print all ADC channel values ------

ADCRW(1,0);
// ADCRW(1,1);
// ADCRW(1,2);
// ADCRW(1,3);
// Serial.println(" --------------------------- "); 
delay(20);  
ADCRW(2,0);
//ADCRW(2,1);
//ADCRW(2,2);
//ADCRW(2,3);
delay(100); 
//SET_POWER23S17(2,0);  // 23S17 alt 


/*

Serial.println(" --------------------------- "); 

// --------------- Arduino-ADCS -----------
// see init-routine for ref-voltage setting
// internal (=1,1 Volt ATMEL-intern) may be the most stable 

// for measuring:
// A0 = I * 1 Ohm, I is the CIC main power supply current
// A1 = U / 20  , U is the CIC main power supply voltage 
// (to be precise: U = A1*20 - A0, because of the voltage drop A0
// A2 = I * 1 Ohm (10 Ohm?), I is the digital coupler power supply current
// A3 = U / 10  , U is the digital coupler power supply voltage
// A4 = foreseen for VCANA (need voltage divider) 
// A5 = foreseen for VCANB (need voltage divider)
// VCANA und VCANB are also measured by the two ADCs on the CIC cards

// syntax:  val = analogRead(analogPin);    // read the input pin

Ard_ADC0 = analogRead(0);
delay(2); 
//It takes about 100 microseconds (0.0001 s) 
// to read an analog input. Delay needed???
Ard_ADC1 = analogRead(1);
delay(2); 
Ard_ADC2 = analogRead(2);
delay(2); 
Ard_ADC3 = analogRead(3);
delay(2); 
// KORREKTUR 4 <> 5  (Dreher im Layout des Adapters?)
Ard_ADC4 = analogRead(5);
delay(2); 
Ard_ADC5 = analogRead(4);


Serial.print("Arduino-ADC0 =");
Serial.print(Ard_ADC0, DEC);  
Serial.print(" >>> I-CIC-PSU = ");
fArd_ADC0 = Ard_ADC0/1023.0; // from counts to ADC-factor
fArd_ADC0 = fArd_ADC0 *1100.0;  // from ADC-factor to Millivolt/Milliampere
Serial.print(fArd_ADC0, 2);  
Serial.println(" mA");  

Serial.print("Arduino-ADC1 =");
Serial.print(Ard_ADC1, DEC);  
Serial.print(" >>> U-CIC-PSU = ");
fArd_ADC1 = Ard_ADC1/1023.0; // from counts to ADC-factor
fArd_ADC1 = fArd_ADC1 *1.1;  // from ADC-factor to Volt
fArd_ADC1 = fArd_ADC1 *20;  // voltage divider factor 
Serial.print(fArd_ADC1, 3);  
Serial.println(" V");  



Serial.print("Arduino-ADC2 =");
Serial.print(Ard_ADC2, DEC);  
Serial.print(" >>> I-DCoupl = ");
fArd_ADC2 = Ard_ADC2/1023.0; // from counts to ADC-factor
fArd_ADC2 = fArd_ADC2 *1100.0;  // from ADC-factor to Millivolt/Milliampere
// check: R = 1 Ohm or 10 Ohm??? If 10 Ohm then div by 10
Serial.print(fArd_ADC2, 2);  
Serial.println(" mA");  


Serial.print("Arduino-ADC3 =");
Serial.print(Ard_ADC3, DEC);  
Serial.print(" >>> U-DCoupl = ");
fArd_ADC3 = Ard_ADC3/1023.0; // from counts to ADC-factor
fArd_ADC3 = fArd_ADC3 *1.1;  // from ADC-factor to Volt
fArd_ADC3 = fArd_ADC3 *10;  // voltage divider factor 
Serial.print(fArd_ADC3, 3);  
Serial.println(" V");  


Serial.print("Arduino-ADC4:=");
Serial.print(Ard_ADC4, DEC);  
Serial.print(" >>> U-VCANA = ");
fArd_ADC4 = Ard_ADC4/1023.0; // from counts to ADC-factor
fArd_ADC4 = fArd_ADC4 *1.1;  // from ADC-factor to Volt
fArd_ADC4 = fArd_ADC4 *4;  // voltage divider factor 4 <<<<
Serial.print(fArd_ADC4, 3);  
Serial.println(" V");  

Serial.print("Arduino-ADC5:=");
Serial.print(Ard_ADC5, DEC);  
Serial.print(" >>> U-VCANB = ");
fArd_ADC5 = Ard_ADC5/1023.0; // from counts to ADC-factor
fArd_ADC5 = fArd_ADC5 *1.1;  // from ADC-factor to Volt
fArd_ADC5 = fArd_ADC5 *4;  // voltage divider factor 4 <<<
Serial.print(fArd_ADC5, 3);  
Serial.println(" V");  

Serial.println("CAN-Test-on");  
*/

/*  
   for (int i=0; i <= 255; i++){
      analogWrite(5, i);
      delay(5);
   } 
*/
analogWrite(5, 64); 
// delay(1500); 
analogWrite(5, 255); 
/*  
 // Send "CAN-Signal", approx. 980 Hz, duty cycle 0..100 % = value 0..255
delay(500); 
   for (int i=255; i >= 10; i--){
      analogWrite(6, i);
      delay(5);
   }
   */
//
analogWrite(6, 192); 
// delay(1500); 
analogWrite(6, 255); 

//Serial.println("CAN-Test-off");  
/*
delay(500); 
*/
// 
//    



//-----------------------POWER OFF -------------

/*
SET_POWER23S08(2,0);  
delay(400 ); 
SET_POWER23S08(1,0);  
delay(200);   
Serial.println(" ====OFF============= "); 

*/

}
