void getTemp(float * t)
{

  // Converts input from a thermistor voltage divider to a temperature value.
  // The voltage divider consists of thermistor Rt and series resistor R0.
  // The value of R0 is equal to the thermistor resistance at T0.
  // You must set the following constants:
  //                  adcMax  ( ADC full range value )
  //                  analogPin (Arduino analog input pin)
  //                  invBeta  (inverse of the thermistor Beta value supplied by manufacturer).
  // Use Arduino's default reference voltage (5V or 3.3V) with this module.
  //

  const int analogPin = 0; // replace 0 with analog pin
  const float invBeta = 1.00 / 3380.00;   // replace "Beta" with beta of thermistor

  const  float adcMax = 1023.00;
  const float invT0 = 1.00 / 298.15;   // room temp in Kelvin

  int adcVal, i, numSamples = 5;
  float  K, C, F;

  adcVal = 0;
  for (i = 0; i < numSamples; i++)
  {
    adcVal = adcVal + analogRead(analogPin);
    delay(100);
  }
  adcVal = adcVal / 5;
  K = 1.00 / (invT0 + invBeta * (log ( adcMax / (float) adcVal - 1.00)));
  C = K - 273.15;                      // convert to Celsius
  F = ((9.0 * C) / 5.00) + 32.00; // convert to Fahrenheit
  t[0] = K; t[1] = C; t[2] = F;
  return;
}

void setup()
{
  analogReference(DEFAULT);
  Serial.begin(9600);
}

void loop()
{
  float temp[3];
  getTemp(temp);

  Serial.print("Temperature is     ");
  Serial.print(temp[0]); Serial.print(" Kelvin      ");
  Serial.print(temp[1]); Serial.print(" deg. C      ");
  Serial.print(temp[2]); Serial.print(" deg. F      ");
  Serial.println();
  delay(2000);
  return;
}


