// inslude the SPI library:
#include <SPI.h>

// set pin 10 as the slave select for the digital pot:
const int CANRXA_Pin = 3;  // receiving CAN data
const int CANRXB_Pin = 4;
const int CANTXA_Pin = 5;  // sending CAN data
const int CANTXB_Pin = 6;
const int MCSA_Pin = 7;   // chip select monitor A = ADC
const int CCSA_Pin = 8;   // chip select control A = power enable register
const int MCSB_Pin = 9;   // chip select monitor B = ADC
const int CCSB_Pin = 10;  // chip select control B = power enable register
const int ledPin = PB5;
bool active = false;
char buffer[100];
int status = 0;
int ledState = LOW;
// MOSI = Slave DIN = 11
// MISO = Slave DOUT = 12
// SCK  = Master-Clock = 13



void setup() {

  analogReference(INTERNAL);
  //type =  (DEFAULT, INTERNAL, INTERNAL1V1, INTERNAL2V56, or EXTERNAL).



  // set the slaveSelectPin as an output:
  pinMode(MCSA_Pin, OUTPUT);
  pinMode(CCSA_Pin, OUTPUT);
  pinMode(MCSB_Pin, OUTPUT);
  pinMode(CCSB_Pin, OUTPUT);
  pinMode(ledPin, OUTPUT);
  pinMode(CANTXA_Pin, OUTPUT);
  pinMode(CANTXB_Pin, OUTPUT);


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

void SET_POWER23S17(int side, int state) {
  int CCS_Pin;
  if (side == 1) CCS_Pin = CCSA_Pin;
  if (side == 2) CCS_Pin = CCSB_Pin;
  digitalWrite(CCS_Pin, LOW);
  delay(1);            // Delay in Millisec
  SPI.transfer(0x40);  // slave adress write  MCP23S17
  delay(1);
  SPI.transfer(0x00);  // reg = IODIRA
  delay(1);
  SPI.transfer(0x00);  // set IODIRA , 1 = inputs / 0 = outputs
  delay(1);
  digitalWrite(CCS_Pin, HIGH);
  delay(4);
  digitalWrite(CCS_Pin, LOW);
  delay(1);            // Delay in Millisec
  SPI.transfer(0x40);  // slave adress write  MCP23S17
  delay(1);
  SPI.transfer(0x12);  // GPIOA
  delay(1);
  SPI.transfer(state);  // set GPIOA
  delay(1);
  digitalWrite(CCS_Pin, HIGH);
}
void SET_POWER23S08(int side, int state) {
  int CCS_Pin;
  if (side == 1) CCS_Pin = CCSA_Pin;
  if (side == 2) CCS_Pin = CCSB_Pin;
  digitalWrite(CCS_Pin, LOW);
  delay(1);            // Delay in Millisec
  SPI.transfer(0x40);  // slave adress write  MCP23S17
  delay(1);
  SPI.transfer(0x00);  // reg = IODIRA
  delay(1);
  SPI.transfer(0x00);  // set IODIRA , 1 = inputs / 0 = outputs
  delay(1);
  digitalWrite(CCS_Pin, HIGH);
  delay(4);
  digitalWrite(CCS_Pin, LOW);
  delay(1);            // Delay in Millisec
  SPI.transfer(0x40);  // slave adress write  MCP23S17
  delay(1);
  SPI.transfer(0x09);  // GPIOA 12 bei 23S17, GPIO 09 bei 23S08
  delay(1);
  SPI.transfer(state);  // set GPIO(A)
  delay(1);
  digitalWrite(CCS_Pin, HIGH);
}

//--------- ADC is CS5525-ARZ, has 4 channels 16 Bit
// already used at CERN, radiation tolerant qualified (ELMB2)
// readout is a bit complex ...

long ADCRW(int side, int channel) {
  // ADC-Init  15 Bytes FF, 1 Byte FE
  int MCS_Pin, channelbyte;
  int i, byte1, byte2, byte3, byte4, byte5, byte6;
  long ADC_value, current_ma;
  float ADC_voltage;
  if (side == 1) MCS_Pin = MCSA_Pin;
  if (side == 2) MCS_Pin = MCSB_Pin;
  digitalWrite(MCS_Pin, LOW);
  for (i = 1; i < 16; i++) {
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
  byte1 = SPI.transfer(0x0b);
  byte2 = SPI.transfer(0x00);
  byte3 = SPI.transfer(0x00);
  byte4 = SPI.transfer(0x00);
  //Serial.print(byte4 , HEX);
  //Serial.print(" - ");   // sollte 0x40 sein
  digitalWrite(MCS_Pin, HIGH);
  delay(1);
  digitalWrite(MCS_Pin, LOW);
  byte1 = SPI.transfer(0x0b);
  byte2 = SPI.transfer(0x00);
  byte3 = SPI.transfer(0x00);
  byte4 = SPI.transfer(0x00);
  //Serial.print(byte4 , HEX);
  //Serial.println(" << Reset soll 40 - 0"); // sollte 0x00 sein
  digitalWrite(MCS_Pin, HIGH);
  delay(1);

  // ADC-configuration
  digitalWrite(MCS_Pin, LOW);
  SPI.transfer(0x03);
  SPI.transfer(0x00);
  SPI.transfer(0x30);  // number of CSRs
  SPI.transfer(0x00);
  delay(1);
  digitalWrite(MCS_Pin, HIGH);

  digitalWrite(MCS_Pin, LOW);  // readback for control
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
  SPI.transfer(0xab);  //  ab statt a9 für 2,5 V statt 5,0 V range in ch 3
  delay(1);
  digitalWrite(MCS_Pin, HIGH);
  delay(2);

  digitalWrite(MCS_Pin, LOW);  // readback for control
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
  channelbyte = (channel * 8);
  channelbyte = channelbyte | 0x81;
  //Serial.print(channelbyte , HEX); Serial.print(": ");
  SPI.transfer(channelbyte);
  digitalWrite(MCS_Pin, HIGH);
  delay(10);

  // ADC-channel  // gain cal.
  digitalWrite(MCS_Pin, LOW);
  delay(10);
  channelbyte = (channel * 8);
  channelbyte = channelbyte | 0x82;
  //Serial.print(channelbyte , HEX); Serial.print(": ");
  SPI.transfer(channelbyte);
  digitalWrite(MCS_Pin, HIGH);
  delay(10);



  // ADC-channel-read
  digitalWrite(MCS_Pin, LOW);
  delay(10);
  channelbyte = (channel * 8);
  channelbyte = channelbyte | 0x80;
  //Serial.print(channelbyte , HEX); Serial.print(": ");
  SPI.transfer(channelbyte);
  byte1 = SPI.transfer(0x00);
  byte2 = SPI.transfer(0x00);
  byte3 = SPI.transfer(0x00);
  byte4 = SPI.transfer(0x00);
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
  byte1 = SPI.transfer(0x00);
  byte2 = SPI.transfer(0x00);
  byte3 = SPI.transfer(0x00);
  byte4 = SPI.transfer(0x00);
  // if (side == 1) Serial.print("A");
  // if (side == 2) Serial.print("B");
  // Serial.print(channel);
  // Serial.print(" ADC: ");
  // Serial.print(byte1, HEX);
  // Serial.print("-");
  // Serial.print(byte2, HEX);
  // Serial.print("-");
  // Serial.print(byte3, HEX);
  // Serial.print("-");
  // Serial.print(byte4, HEX);
  // Serial.print(" = value dec ");
  ADC_value = (256L * byte2) + byte3;
  // Serial.print(ADC_value, DEC);
  // ADC_voltage = ADC_value;
  // ADC_voltage = ADC_voltage / 65535;
  // ADC_voltage = ADC_voltage * 2.5;
  // Serial.print(" = voltage  ");
  // Serial.print(ADC_voltage, DEC);
  // if (channel == 1) {
  // current_ma = 1000 * ADC_voltage;
  //   // Serial.print(" = current/mA  ");
  //   Serial.print(current_ma, DEC);
  // }


  // Serial.println(" << ");
  delay(1);
  digitalWrite(MCS_Pin, HIGH);
  delay(1);


  return ADC_value;
}

float canReadBackTest(int dutyCycleDec) {
  analogWrite(CANTXA_Pin, dutyCycleDec);
  // delay(500);
  unsigned long highTime = pulseIn(CANRXB_Pin, HIGH);
  unsigned long lowTime = pulseIn(CANRXB_Pin, LOW);
  unsigned long cycleTime = highTime + lowTime;
  return (float)highTime / float(cycleTime);
}

void loop() {
  // put your main code here, to run repeatedly:
  if ((Serial.available() > 0)) {
    status = Serial.read();
    //Serial.print(status);
  }
  if (status == 1 && !active) {
    active = !active;

    SET_POWER23S08(2, 03);  // 23S17 alt
    delay(200);
    //SET_POWER23S17(1,255);  // 23S17 alt
    delay(200);
    SET_POWER23S08(1, 03);
    delay(4000);
    ledState = HIGH;
    analogWrite(5, 112);
    delay(500);
    analogWrite(5, 255);
    // Send "CAN-Signal", approx. 980 Hz, duty cycle 0..100 % = value 0..255
    delay(500);
    analogWrite(6, 144);
    delay(500);
    analogWrite(6, 255);
    delay(500);
  } else if (status == 2 && active) {
    active = !active;
    ledState = LOW;
    SET_POWER23S08(2, 0);
    delay(200);
    //SET_POWER23S17(1,0);  // 23S17 alt
    delay(200);
    SET_POWER23S08(1, 0);
    delay(200);
  } else if (active) {
    ledState = HIGH;
    float dutyCycle = canReadBackTest(123);
    char dutyCycleString[4];
    dtostrf(dutyCycle, 4, 2, dutyCycleString);
    sprintf(buffer, "%ld;%ld;%ld;%ld;%ld;%ld;%ld;%ld;%d;%d;%d;%d;%d;%d;%c%c%c%c\n", 
      ADCRW(1, 0), //U-VCANA
      ADCRW(1, 1), //I-VCANA
      ADCRW(1, 2), //V-MOPSA
      ADCRW(1, 3), //V-NTCA
      ADCRW(2, 0), //U-VCANB
      ADCRW(2, 1), //I-VCANB
      ADCRW(2, 2), //V-MOPSB
      ADCRW(2, 3), //U-NTCB
      analogRead(0), //I-CIC_PSU
      analogRead(1), //U-CIC_PSU
      analogRead(2), //I-DCoupl
      analogRead(3), //U-DCoupl
      analogRead(5), //U-VCANA
      analogRead(4), //U-VCANB
      dutyCycleString[0],dutyCycleString[1],dutyCycleString[2],dutyCycleString[3]);
    Serial.print(buffer);
  } else {
    ledState = LOW;
    SET_POWER23S08(2, 0);
    delay(200);
    //SET_POWER23S17(1,0);  // 23S17 alt
    delay(200);
    SET_POWER23S08(1, 0);
    delay(200);
  }
  digitalWrite(ledPin, ledState);
}
