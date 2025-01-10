
int Uout_analogPin = 0;
int Uiout_analogPin = 1;
int Uin_analogPin = 2;



int val = 0;           // variable to store the value read
float Uout, Uiout, Iout, Uin;

void setup()
{
  Serial.begin(9600);          //  setup serial
  analogReference(INTERNAL);   // Uref int = 1,1 V

pinMode(A0, INPUT);  // be sure to define the ADC pind as input WITHOUT pullup INPUT_PULLUP
pinMode(A1, INPUT);
pinMode(A2, INPUT);
pinMode(A3, INPUT);
pinMode(A4, INPUT);
pinMode(A5, INPUT);

PORTC = 0;  // all PORTC pins low, because no pullup for A0..A5
}


void loop()
{
  val = analogRead(Uout_analogPin);    // read the input pin
  Uout = val * 1.1 / 1024;  //  internal reference 1.1 V
  Uout = Uout * 5.662;   //  old: 5.7/1.0 ;  // voltage divider 4k7 and 1k0
//  Serial.print("val = ");
//  Serial.print(val);             // debug value
//  Serial.print(" Uout(V): ");
  Serial.print(Uout);  
  // resolution is 0.006 V         
  delay(100);

  val = analogRead(Uiout_analogPin);    // read the input pin
  Uiout = val * 1.1 / 1024;  //  internal reference 1.1 V
  Iout = Uiout * 10.000 ;  // shunt resistor 0,1 Ohm (5 %) means 0.1 V = 1000 mA
                        // measured resistance approx 0.105??? Ohm
//  Serial.print("val = ");
//  Serial.print(val);             // debug value
//  Serial.print(" Uiout(V): ");
//  Serial.println(Uiout);  
//  Serial.print(" Iout(A): ");
  Serial.print(",");   
  Serial.print(Iout);  
  // resolution is 0.01 A 
  delay(100);

  val = analogRead(Uin_analogPin);    // read the input pin
  Uin  = val * 1.1 / 1024;  //  internal reference 1.1 V
  Uin  = Uin * 28.120 ; // old  28.4/1.00 ;  // voltage divider 27.4 k and 1k0
//  Serial.print("val = ");
//  Serial.print(val);             // debug value
//  Serial.print(" Uin(V): ");
  Serial.print(",");   
  Serial.println(Uin);  
  // resolution is 0.03 V         
//  delay(100);
 

//  Serial.println("------------");             // debug value
  delay(800);

}
