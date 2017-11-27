/* ~~~~ Simple Real Time Teensy Analog Out Stim ~~~~
   Notes: Teensey 3.5/3.6 has two built in 12 bit dacs.
   I assume you have a 3.5 or 3.6 and have 2 outs. But you can easily go to 1.
   I use the builtin FlexiTimer2 to handle the interupts for timing.

   v0.96
   11/27/2017
   cdeister@brown.edu
*/

#include <FlexiTimer2.h>

// session params
int sampsPerSecond = 5000; // samples per second (works well up to 5K, 10-20K with effort)
float evalEverySample = 1.0; // number of times to poll the stim funtion
int trigTime = 0.01 * sampsPerSecond;

// initialize counters
float stateCounterA = 0;
float stateCounterB = 0;
int pulseCounterA = 0;
int pulseCounterB = 0;
float tTime = 0;
float initArTime;

int pulsing=0;

// train vals that get set in python
int c1 = 0;
int c2 = 0;
int c3 = 0;

char knownHeaders[] = {'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l'};
int knownReset[] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
int knownValues[] = { -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1};
int varRec = 0;

// init vars
int pyState = knownValues[0];

int  pulseTimeA = knownValues[1];
int  delayTimeA = knownValues[2];
int  stimAmp_chanA = knownValues[3];
int  nPulseA = knownValues[4];
int baselineA = knownValues[5];

int  pulseTimeB = knownValues[6];
int  delayTimeB = knownValues[7];
int stimAmp_chanB = knownValues[8];
int  nPulseB = knownValues[9];
int baselineB = knownValues[10];

int trainDur = knownValues[11];





bool sBit = 0;

// if you want to add delays it has to be counterbased
int serialDelay = 0.1 * sampsPerSecond;
int serDelayCounter = 0;


// general variable
int readValA;
int readValB;

int trigAVal = 0;

int writeValA = 0;
int writeValB = 0;




// boolean toggles
bool feedbackVal = 0;
bool feedbackValB = 0;
bool inPulseA = 0;
bool inPulseB = 0;
bool baselineAComp = 0;
bool baselineBComp = 0;
bool scopeTriggered = 0;
bool flushState = 0;

// analog outputs
const int dacPinA = A21;
const int dacPinB = A22;

// analog inputs
const int dacReadA = A9;
const int dacReadB = A8;

// feedback LEDs
const int pulseA_LED = 13;
const int pulseB_LED = 14;

// triggers
const int scopeTrigger = 6;


void setup() {

  Serial.begin(115200);
  delay(2);
  analogWriteResolution(12);
  pinMode(pulseA_LED, OUTPUT);
  pinMode(pulseB_LED, OUTPUT);
  pinMode(scopeTrigger, OUTPUT);
  FlexiTimer2::set(1, evalEverySample / sampsPerSecond, fStim); // call ever
  FlexiTimer2::start();
}



void fStim() {

  // always look for new info from python.
  bool p = flagReceive();
  if (p == 1) {

    assignVars();
    spitVars();

  }





  // **********************************
  // STATE #O is the reset/rest state.
  // **********************************

  if (pyState == 0) {
    while (Serial.available()){
      Serial.read();
    }
    tTime = 0;

    stateCounterA = 0;
    stateCounterB = 0;

    pulseCounterA = 0;
    pulseCounterB = 0;


    flushState = 0;

    initArTime = millis();
    sBit = 0;
    assignVars();
    feedbackVal = 0;
    feedbackValB = 1;
    inPulseA = 0;
    inPulseB = 0;
    baselineAComp = 0;
    baselineBComp = 0;
    scopeTriggered = 0;
    writeValA = 0;
    writeValB = 0;

  }



  // **********************************
  // STATE #1 is the init state.
  // **********************************
  else if (pyState == 1) {


  }

  else if (pyState == 2) {

    // always increment time and see if we are out of it
    tTime = tTime + 1;
    if (tTime <= trainDur) {
      pulsing=1;

      // **************************
      // a) ----  trigger stuff
      // **************************

      if (tTime <= trigTime) {
        digitalWrite(scopeTrigger, 1);
      }

      else if (tTime > trigTime) {
        digitalWrite(scopeTrigger, 0);
      }

      // **************************
      // END -  trigger stuff
      // **************************

      // ******************************
      // b) ----  channel 1 pulse tain
      // ******************************
      // baseline a
      if (tTime <= baselineA) {
        inPulseA = 0;
        stateCounterA = 0;
      }

      else if (tTime > baselineA && baselineAComp == 0) {
        inPulseA = 1;
        stateCounterA = 0;
        baselineAComp = 1;
      }

      // channel a IPI
      if (inPulseA == 0) {
        stateCounterA = stateCounterA + 1;
        if (stateCounterA <= delayTimeA) {
          feedbackVal = 0;
          writeValA = 0;
        }

        // exit A
        else if (stateCounterA > delayTimeA) {
          stateCounterA = 0;
          pulseCounterA = pulseCounterA + 1;
          if (pulseCounterA <= nPulseA) {
            inPulseA = 1;
          }
          else if (pulseCounterA > nPulseA) {
            inPulseA = 0;
          }
        }
      }

      // pulse state A
      if (inPulseA == 1) {
        stateCounterA = stateCounterA + 1;
        if (stateCounterA <= pulseTimeA) {
          feedbackVal = 1;
          writeValA = stimAmp_chanA;
        }

        // exit A
        else if (stateCounterA > pulseTimeA) {
          stateCounterA = 0;
          inPulseA = 0;
        }
      }
      // ******************************
      // END -  channel 1 pulse tain
      // ******************************

      // ******************************
      // c) ----  channel 2 pulse tain
      // ******************************
      // baseline b
      if (tTime <= baselineB) {
        inPulseB = 0;
        stateCounterB = 0;
      }

      else if (tTime > baselineB && baselineBComp == 0) {

        inPulseB = 1;
        stateCounterB = 0;
        baselineBComp = 1;
      }

      // channel B IPI
      if (inPulseB == 0) {
        stateCounterB = stateCounterB + 1;
        if (stateCounterB <= delayTimeB) {
          feedbackValB = 0;
          writeValB = 0;
        }

        // exit A
        else if (stateCounterB > delayTimeB) {
          stateCounterB = 0;
          pulseCounterB = pulseCounterB + 1;
          if (pulseCounterB <= nPulseB) {
            inPulseB = 1;
          }
          else if (pulseCounterB > nPulseB) {
            inPulseB = 0;
          }
        }
      }

      // pulse state B
      if (inPulseB == 1) {

        stateCounterB = stateCounterB + 1;
        if (stateCounterB <= pulseTimeB) {
          feedbackValB = 1;
          writeValB = stimAmp_chanB;
          sBit = 1;
        }

        // exit A
        else if (stateCounterB > pulseTimeB) {
          stateCounterB = 0;
          inPulseB = 0;
        }
      }
      // ******************************
      // END -  channel 2 pulse tain
      // ******************************

      // *************************************
      // d) ----  write out and update python
      // **************************************

      analogWrite(dacPinA, writeValA);
      analogWrite(dacPinB, writeValB);
      readValA = analogRead(dacReadA);
      readValB = analogRead(dacReadB);
      digitalWrite(pulseA_LED, feedbackVal);
      digitalWrite(pulseB_LED, feedbackValB);
      spitData();
    }

    else if (tTime>trainDur){
      pulsing=0;
      spitData();
      analogWrite(dacPinA, 0);
      analogWrite(dacPinB, 0);
      readValA = analogRead(dacReadA);
      readValB = analogRead(dacReadB);
      digitalWrite(pulseA_LED, 0);
      digitalWrite(pulseB_LED, 0);
    }
  }
}

void loop()
{
}


void spitVars() {

  Serial.print("vars");
  Serial.print(',');
  Serial.print(pyState);
  Serial.print(',');
  Serial.print(pulseTimeA);
  Serial.print(',');
  Serial.print(delayTimeA);
  Serial.print(',');
  Serial.print(stimAmp_chanA);
  Serial.print(',');
  Serial.print(nPulseA);
  Serial.print(',');
  Serial.print(baselineA);
  Serial.print(',');
  Serial.print(pulseTimeB);
  Serial.print(',');
  Serial.print(delayTimeB);
  Serial.print(',');
  Serial.print(stimAmp_chanB);
  Serial.print(',');
  Serial.print(nPulseB);
  Serial.print(',');
  Serial.print(baselineB);
  Serial.print(',');
  Serial.println(trainDur);

}


void spitData() {
  Serial.print("data");
  Serial.print(',');
  Serial.print(tTime);
  Serial.print(',');
  Serial.print(writeValA);
  Serial.print(',');
  Serial.print(writeValB);
  Serial.print(',');
  Serial.print(readValA);
  Serial.print(',');
  Serial.print(readValB);
  Serial.print(',');
  Serial.print(millis() - initArTime);
  Serial.print(',');
  Serial.println(pulsing);
}

void clearBuffer() {
  while (Serial.available()) {
    Serial.read();
  }
}

bool flagReceive() {
  static boolean recvInProgress = false;
  static byte ndx = 0;

  char endMarker = '>';
  char rc;


  int nVal;

  const byte numChars = 32;
  char writeChar[numChars];
  bool newData = 0;
  int selectedVar = 0;



  while (Serial.available() > 0 && newData == 0) {


    rc = Serial.read();


    if (recvInProgress == false) {
      for ( int i = 0; i < 12; i++) {
        if (rc == knownHeaders[i]) {
          selectedVar = i;
          recvInProgress = true;
          Serial.println(selectedVar);
          //          c1 = 1;
        }
      }
    }


    else if (recvInProgress == true) {
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
        newData = 1;

        nVal = int(String(writeChar).toInt());
        c1 = 3;
        c2 = nVal;
        knownValues[selectedVar] = nVal;
        knownReset[selectedVar] = 1;

      }
    }
  }
  return newData;


}


void assignVars() {

  pyState = knownValues[0];
  pulseTimeA = knownValues[1];
  delayTimeA = knownValues[2];
  stimAmp_chanA = knownValues[3];
  nPulseA = knownValues[4];
  baselineA = knownValues[5];
  pulseTimeB = knownValues[6];
  delayTimeB = knownValues[7];
  stimAmp_chanB = knownValues[8];
  nPulseB = knownValues[9];
  baselineB = knownValues[10];
  trainDur = knownValues[11];

}

void resetVars() {
  for ( int i = 0; i < 12; i++) {
    knownReset[i] = 0;
    knownValues[i] = -1;
  }
}

