/* ~~~~ Simple Teensy Analog Out Stim ~~~~
   Notes: Teensey 3.5/3.6 has two built in 12 bit dacs.
   I assume you have a 3.5 or 3.6 and have 2 outs. But you can easily go to 1.
   I use the builtin FlexiTimer2 to handle the interupts for timing.

   v1.0
   cdeister@brown.edu
*/

#include <FlexiTimer2.h>

float stateCounter = 0;
float sTime = 0;
float tTime = 0;
bool itHead = 0;
bool fbVal;
int sampsPerSecond = 5000; // samples per second
float evalEverySample = 1.0; // number of times to poll the stim funtion
int pulseTime = 0.005 * sampsPerSecond;
int delayTime = 0.1 * sampsPerSecond;
float writeValA = 0;
float writeValB = 0;
int readValA;
float trLen = 10 * sampsPerSecond;
int aVal = 0;
int bVal = 0;
bool inPulse = 0;
bool inTrial = 0;
bool varSet = 0;
bool aSet = 0;
bool pSet = 0;


int curState = 0;

int tPyState = 0;
int  lastState;

const int dacPinA = A21;
const int dacPinB = A22;
const int dacReadA = A9;

const int led_pin = 13;     // default to pin 13

/* vars for split read */

//const byte numChars = 32;
//char receivedChars[numChars];
boolean newData = false;




void setup() {
  Serial.begin(115200);
  delay(2);
  analogWriteResolution(12);
  pinMode(led_pin, OUTPUT);
  FlexiTimer2::set(1, evalEverySample / sampsPerSecond, fStim); // call every 500 1ms "ticks"
  FlexiTimer2::start();
}

void fStim() {
  spitVars();
  tPyState = flagReceive('s', '>', tPyState);
  

  if (tPyState == 0) {
    tTime = 0;
    aSet=0;
    pSet=0;
    inPulse = 0;
    stateCounter=0;
    pulseTime=0;
    aVal=0;
  }



  // state 1 is the reset state
  if (tPyState == 1) {
    if (aSet == 0) {
      while (aVal == 0) {
        spitVars();
        aVal = flagReceive('a', '>', aVal);
      }
      aSet = 1;
    }

    if (pSet == 0) {
      while (pulseTime == 0) {
        spitVars();
        pulseTime = flagReceive('p', '>', pulseTime);
      }
      pSet = 1;
    }
  }


  if (tPyState == 2) {
    
    // delay state
    tTime = tTime + 1;
    if (inPulse == 0) {
      stateCounter = stateCounter + 1;
      if (stateCounter <= delayTime) {
        fbVal = 0;
        writeValA = 0;
        writeValB = 0;
        analogWrite(dacPinA, writeValA);
        readValA = analogRead(dacReadA);
        analogWrite(dacPinB, writeValB);
        digitalWrite(led_pin, fbVal);
      }

      // exit
      else if (stateCounter > delayTime) {
        stateCounter = 0;
        inPulse = 1;
      }
    }

    // pulse state
    if (inPulse == 1) {
      stateCounter = stateCounter + 1;
      if (stateCounter <= pulseTime) {
        fbVal = 1;
        writeValA = aVal;
        writeValB = bVal;
        analogWrite(dacPinA, writeValA);
        readValA = analogRead(dacReadA);
        analogWrite(dacPinB, writeValB);
        digitalWrite(led_pin, fbVal);
      }

      // exit
      else if (stateCounter > pulseTime) {
        stateCounter = 0;
        inPulse = 0;
      }
    }
    spitData();
  }
}

void loop()
{
}


void spitVars() {
  Serial.print("vars");
  Serial.print(',');
  Serial.print(aSet);
  Serial.print(',');
  Serial.print(pSet);
  Serial.print(',');
  Serial.println(tPyState);
}



void spitData() {
  Serial.print("data");
  Serial.print(',');
  Serial.print(writeValA);
  Serial.print(',');
  Serial.print(readValA);
  Serial.print(',');
  Serial.print(tTime);
  Serial.print(',');
  Serial.println(tPyState);
}


int flagReceive(char startChars, char endChars, int targVar) {
  static boolean recvInProgress = false;
  static byte ndx = 0;
  char startMarker = startChars;
  char endMarker = endChars;
  char rc;
  bool notRight = 0;
  int nVal = targVar;
  const byte numChars = 32;
  char writeChar[numChars];

  while (Serial.available() > 0 && newData == false && notRight == 0) {
    rc = Serial.read();

    if (recvInProgress == true) {
      if (rc != endMarker) {
        writeChar[ndx] = rc;
        ndx++;
        if (ndx >= numChars) {
          ndx = numChars - 1;
        }
      }
      else if (rc == endMarker ) {
        writeChar[ndx] = '\0'; // terminate the string
        recvInProgress = false;
        ndx = 0;
        //        newData = true;
        nVal = int(String(writeChar).toInt());
      }
    }
    else if (rc == startMarker) {
      recvInProgress = true;
    }
    else if (recvInProgress == false) {
      notRight = 1;
    }
  }
  return nVal;
}
