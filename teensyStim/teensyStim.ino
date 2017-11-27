/* ~~~~ Simple Teensy Analog Out Stim ~~~~
   Notes: Teensey 3.5/3.6 has two built in 12 bit dacs.
   I assume you have a 3.5 or 3.6 and have 2 outs. But you can easily go to 1.
   I use the builtin FlexiTimer2 to handle the interupts for timing.

   v1.0
   cdeister@brown.edu
*/

#include <FlexiTimer2.h>

// session params
int sampsPerSecond = 1000; // samples per second
float evalEverySample = 1.0; // number of times to poll the stim funtion
int trigTime = 0.01 * sampsPerSecond;

// initialize counters
float stateCounterA = 0;
float stateCounterB = 0;
int pulseCounterA = 0;
int pulseCounterB = 0;
float tTime = 0;
float initArTime;

// train vals that get set in python
int pulseTimeA = 0;
int delayTimeA = 0;
int stimAmp_chanA = 0;
int nPulseA = 0;
int baselineA = 0;

int pulseTimeB = 0;
int delayTimeB = 0;
int stimAmp_chanB = 0;
int nPulseB = 0;
int baselineB = 0;

int trainDur = 0;

// train python states
bool bSet = 0;
bool cSet = 0;
bool dSet = 0;
bool eSet = 0;
bool fSet = 0;
bool gSet = 0;
bool hSet = 0;
bool iSet = 0;
bool jSet = 0;
bool kSet = 0;
bool lSet = 0;
bool mSet = 0;

bool sBit = 0;
int serialDelay = 0.1 * sampsPerSecond;
int serDelayCounter = 0;


// general variable
int readValA;
int readValB;
int trigAVal = 0;
int writeValA = 0;
int writeValB = 0;
int pyState = 0;


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

  Serial.begin(19200);
  delay(2);
  analogWriteResolution(12);
  pinMode(pulseA_LED, OUTPUT);
  pinMode(pulseB_LED, OUTPUT);
  pinMode(scopeTrigger, OUTPUT);
  FlexiTimer2::set(1, evalEverySample / sampsPerSecond, fStim); // call ever
  FlexiTimer2::start();
}

void fStim() {

  pyState = flagReceive('a', '>', pyState);


  if (pyState == 0) {
    if (serDelayCounter >= serialDelay) {
      spitVars();
      serDelayCounter = 0;
    }

    tTime = 0;

    stateCounterA = 0;
    stateCounterB = 0;

    pulseCounterA = 0;
    pulseCounterB = 0;



    bSet = 0;
    cSet = 0;
    dSet = 0;
    eSet = 0;
    fSet = 0;
    gSet = 0;
    hSet = 0;
    iSet = 0;
    jSet = 0;
    kSet = 0;
    lSet = 0;
    mSet = 0;

    flushState = 0;

    initArTime = millis();
    sBit = 0;
    pulseTimeA = -1;
    delayTimeA = -1;
    stimAmp_chanA = -1;
    nPulseA = -1;
    baselineA = -1;

    pulseTimeB = -1;
    delayTimeB = -1;
    stimAmp_chanB = -1;
    nPulseB = -1;
    baselineB = -1;

    trainDur = -1;

    feedbackVal = 0;
    feedbackValB = 1;
    inPulseA = 0;
    inPulseB = 0;
    baselineAComp = 0;
    baselineBComp = 0;
    scopeTriggered = 0;
    writeValA = 0;
    writeValB = 0;
    serDelayCounter = serDelayCounter + 1;
    if (flushState == 0) {
      clearBuffer();
      flushState = 1;
    }

  }



  
  if (pyState == 1) {
    spitVars();
    stimAmp_chanA = flagReceive('b', '>', stimAmp_chanA);
    pulseTimeA = flagReceive('c', '>', pulseTimeA);
    delayTimeA = flagReceive('d', '>', delayTimeA);
    nPulseA = flagReceive('e', '>', nPulseA);
    baselineA = flagReceive('f', '>', baselineA);
    trainDur = flagReceive('g', '>', trainDur);
    stimAmp_chanB = flagReceive('h', '>', stimAmp_chanB);
    pulseTimeB = flagReceive('i', '>', pulseTimeB);
    delayTimeB = flagReceive('j', '>', delayTimeB);
    nPulseB = flagReceive('k', '>', nPulseB);
    baselineB = flagReceive('l', '>', baselineB);




    if (bSet == 0) {
//      stimAmp_chanA = flagReceive('b', '>', stimAmp_chanA);
      if (stimAmp_chanA != -1) {
        bSet = 1;
      }
    }

    if (cSet == 0) {
//      pulseTimeA = flagReceive('c', '>', pulseTimeA);
      if (pulseTimeA != -1) {
        cSet = 1;
      }
    }

    if (dSet == 0) {
//      delayTimeA = flagReceive('d', '>', delayTimeA);
      if (delayTimeA != -1) {
        dSet = 1;
      }
    }
    if (eSet == 0) {
//      nPulseA = flagReceive('e', '>', nPulseA);
      if (nPulseA != -1) {
        eSet = 1;
      }
    }

    if (fSet == 0) {
//      baselineA = flagReceive('f', '>', baselineA);
      if (baselineA != -1) {
        fSet = 1;
      }
    }
    if (gSet == 0) {
//      trainDur = flagReceive('g', '>', trainDur);
      if (trainDur != -1) {
        gSet = 1;
      }
    }
    if (hSet == 0) {
//      stimAmp_chanB = flagReceive('h', '>', stimAmp_chanB);
      if (stimAmp_chanB != -1) {
        hSet = 1;
      }
    }
    if (iSet == 0) {
//      pulseTimeB = flagReceive('i', '>', pulseTimeB);
      if (pulseTimeB != -1) {
        iSet = 1;
      }
    }
    if (jSet == 0) {
//      delayTimeB = flagReceive('j', '>', delayTimeB);
      if (delayTimeB != -1) {
        jSet = 1;
      }
    }
    if (kSet == 0) {
//      nPulseB = flagReceive('k', '>', nPulseB);
      if (nPulseB != -1) {
        kSet = 1;
      }
    }
    if (lSet == 0) {
//      baselineB = flagReceive('l', '>', baselineB);
      if (baselineB != -1) {
        lSet = 1;
      }
    }
//    serDelayCounter = serDelayCounter + 1;
  }

  if (pyState == 2) {

    spitVars();
    // always increment time and see if we are out of it
    tTime = tTime + 1;
    if (tTime <= trainDur) {

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
  Serial.print(bSet);
  Serial.print(',');
  Serial.print(cSet);
  Serial.print(',');
  Serial.print(dSet);
  Serial.print(',');
  Serial.print(eSet);
  Serial.print(',');
  Serial.print(fSet);
  Serial.print(',');
  Serial.print(gSet);
  Serial.print(',');
  Serial.print(hSet);
  Serial.print(',');
  Serial.print(iSet);
  Serial.print(',');
  Serial.print(jSet);
  Serial.print(',');
  Serial.print(kSet);
  Serial.print(',');
  Serial.println(lSet);
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
  Serial.println(baselineA);
}

void clearBuffer() {
  while (Serial.available()) {
    Serial.read();
  }
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
  bool newData = false;

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
