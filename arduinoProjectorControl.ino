
/* Arduino Projector Control
  Elizabeth Adelaide, March, 2017
  Comissionsed by Robin Cameron
  Controls a relay to advance seven carousel projectors in a series
  Reads serial input from a python GUI to stop, pause, resume and change timing
  Full code and documentation can be found here: https://github.com/elizabethadelaide/robinProjectorControl
  */
#include<EEPROM.h>
#define NUMPROJS 7

int projectorPins[NUMPROJS] = {2,3,4,5,6,7, 8};
int timer[NUMPROJS] = {1000, 1000, 1000, 1000, 1000, 1000, 5000}; //time between each relay

int cascadeTime = 500; //time between each projector
int cycleTime = 10000; //time to start a new cycle

int clickTime = 250; //time to click down

const byte numChars = 32;
char receivedChars[numChars];

boolean newData = false;

//for EEPROM
int eeaddress = 0; //start from byte 0
int value[512];

void setup() {
  // put your setup code here, to run once:
  int i;
  int m;
  int temp;
  
  //initialize serial:
  Serial.begin(9600);
  
  //initialize projector pins
  for(i = 0; i < NUMPROJS; i++){
     pinMode(projectorPins[i], OUTPUT);
     digitalWrite(projectorPins[i], HIGH); //relays are open with high input
  }
  
  while (eeaddress < 45){
    value[eeaddress] = EEPROM.read(eeaddress);
    if (value[eeaddress] == '\n'){ //EOF
      break;
    }
    eeaddress = eeaddress + 1;
  }
  
  if (eeaddress == 28){ //correctly read/valid data
    eeaddress = 0;
    for (i = 0; i < NUMPROJS; i++){
      temp = 0;
      for (m = 0; m < 4; m++){
        temp = temp + (value[eeaddress] * pow(255,m));
        eeaddress++;
      }
      timer[i] = temp;
      if (timer[i] < 0){
         for (i = 0; i < NUMPROJS; i++){timer[i] = 1000; }
         break;
      }
    }
  }
  
}

void loop() {
  // put your main code here, to run repeatedly:
  int i;
  int ind;
  
  //go through each projector:
  for (i = 0; i < NUMPROJS; i++){
    receiveData();
    ind = processData(i);
    showNewData();
  
    //Serial.print("Ind: ");
    Serial.print(ind, DEC);
    Serial.print("\n");
    //Serial.println(i);
    
    switch(ind){
      case 10: //stop
        ind = stopProj();
        i = 0;
        break; 
      case 13: //rewrite times
        Serial.println("Rewrite");
        rewriteTimes();
        break;
      case 11: //pause
        ind = stopProj();
        i = i;
        break;
     
      default:
    
     break;
    }
    digitalWrite(projectorPins[i], LOW);
        
    delay(clickTime);//give enough time to click
    digitalWrite(projectorPins[i], HIGH);
    delay(timer[i]);
  }
}

int rewriteTimes(){
  int i;
  int m;
  int newCascadeTime = 0;
  int newCycleTime = 0;
  int temp;
  uint8_t writevalue;
  
  for (i = 2; i <= 5; i++){
    temp = ((int)((uint8_t)receivedChars[i]));
    newCascadeTime += temp* pow(256, 5-i);

  }
  Serial.print("\n");
  for (i = 6; i <= 9; i++){
      temp = ((int)((uint8_t)receivedChars[i]));
    newCycleTime += temp* pow(256, 9-i);

  }
  cycleTime = newCycleTime;
  cascadeTime = newCascadeTime;
  
  if (cycleTime < NUMPROJS*cascadeTime){
    cycleTime = NUMPROJS * cascadeTime;
  }
  if (cycleTime < NUMPROJS*clickTime){
    cycleTime = NUMPROJS * clickTime;
  }

  for (i = 0; i < NUMPROJS- 1; i++){
       timer[i] = cascadeTime - clickTime;
    }
    //time between starting a new cycle
    timer[NUMPROJS - 1] = ((cycleTime) - ((NUMPROJS -1) * cascadeTime)) - clickTime;
    
  eeaddress = 0;
  //Write to EEPROM/
  for (i = 0; i < NUMPROJS; i++){
    temp = timer[i];
    for (m = 0; m < 4; m++){
      writevalue = temp % 255;
      temp = floor(temp / pow(255,m+1));
      EEPROM.write(eeaddress, writevalue);
      eeaddress++;
    }
  }
  EEPROM.write(eeaddress, '\n');
}
  

int stopProj(){
  int ind = 10;
  
  //Serial.println("Stopped");
  while (ind != 12){
    //Serial.println(ind);
    //delay(500);
    receiveData();
    ind = processData(ind);
    showNewData();
    
    if (ind >= 0 && ind < NUMPROJS){
      digitalWrite(projectorPins[ind], LOW);
      delay(clickTime);
      digitalWrite(projectorPins[ind], HIGH);
      ind = 10;
    }
  }
  return ind;
}

int processData(int index){
  int indicator;
   int i;
   
   indicator = index;
   
   
   if (newData){
     //Serial.println("Indicator");
     indicator = 10*((int)receivedChars[0] - 48)+ ((int)receivedChars[1] - 48);
   
     Serial.print("Indicator");
     Serial.print(indicator);
     Serial.print('\n');
     delay(500);

   }
   
   return indicator;
}
   
void receiveData(){
  static byte ndx = 0;
  char endMarker = '\n';
  char rc;
  
  //Serial.println(Serial.available());
  //Serial.println(newData);
  while (Serial.available() > 0 && newData == false){
    //Serial.println("info received");
    rc = Serial.read();
    if (rc!= endMarker){
       receivedChars[ndx] = rc;
       ndx++;
       if (ndx >= numChars){
          ndx = numChars - 1;
       }
    }
    else{
      receivedChars[ndx] = '\0'; 
      ndx = 0;
      newData = true;
    }
  }
}

void showNewData() {
 if (newData == true) {
   Serial.print("Received:");
   Serial.println(receivedChars);
   
   newData = false;
 }
}


