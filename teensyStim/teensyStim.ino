/* ~~~~ Simple Real Time Teensy Analog Out Stim ~~~~
   Notes: Teensey 3.5/3.6 has two built in 12 bit dacs.
   I assume you have a 3.5 or 3.6 and have 2 outs. But you can easily go to 1.
   I use the builtin FlexiTimer2 to handle the interupts for timing.
   v1.1 - more arrays; fewer problems
   11/27/2017
   cdeister@brown.edu
   # Anything that is licenseable is governed by an MIT License in the github directory.
*/

#include <FlexiTimer2.h>

// Hardware Params
int adcResolution = 12; // in bits; res of ADCs
int dacResolution = 12; // in bits; res of DACs

// session params
int sampsPerSecond = 1000; // samples per second
float evalEverySample = 1.0; // number of times to poll the stim funtion
int trigTime = 0.01 * sampsPerSecond;

// Initialize counter and mc time.
float tTime = 0;
float initArTime;

// jank variables
int pulsing = 0;

// train vals that we look for (set elsewhere; python)
char knownHeaders[] = {'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n'};
int knownValues[] = { -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1};



// init vars
int pyState = knownValues[0];
int pulseTimeA = knownValues[1];
int delayTimeA = knownValues[2];
int stimAmp_chanA = knownValues[3];
int nPulseA = knownValues[4];
int baselineA = knownValues[5];

int pulseTimeB = knownValues[6];
int delayTimeB = knownValues[7];
int stimAmp_chanB = knownValues[8];
int nPulseB = knownValues[9];

int baselineB = knownValues[10];
int trainDur = knownValues[11];



// analog outputs
int dacChans[] = {A21, A22};
int writeValues[] = {0, 0};
int chanAStates[] = {0, 0, 0, 0};
int chanBStates[] = {0, 0, 0, 0};

// analog inputs
int adcChans[] = {A9, A8, A5, A4, A3, A2};
int readValues[] = {0, 0, 0, 0, 0, 0};


// digital outs
const int scopeTrigger = 6;
int counterChans[] = {25, 13}; //13 is 24
int counterValues[] = {0, 0};
int counterInts[] = {-1,-1}; // in samples
int counterAStates[] = {0, 0, 0, 0};
int counterBStates[] = {0, 0, 0, 0};



bool scopeTriggered = 0;
bool flushState = 0;


void setup() {

  Serial.begin(115200);
  delay(2);

  analogWriteResolution(dacResolution);
  analogReadResolution(adcResolution);


  for ( int i = 0; i < 2; i++) {
    pinMode(counterChans[i], OUTPUT);
  }


  pinMode(scopeTrigger, OUTPUT);
  FlexiTimer2::set(1, evalEverySample / sampsPerSecond, fStim); // call ever
  FlexiTimer2::start();

}

// pyStim is interrupt based
// so fStim is the main "loop"
// we have to time a function, not run a loop.

void fStim() {


  // always look for new info from python.
  bool p = flagReceive(knownHeaders, knownValues);
  if (p == 1) {

    assignVars();
    spitVars();

  }

  // **********************************
  // STATE #O is the reset/rest state.
  // **********************************

  if (pyState == 0) {
    while (Serial.available()) {
      Serial.read();
    }
    resetVars();
    tTime = 0;
    flushState = 0;
    assignVars();
    pulsing = 0; // super jank

    
    scopeTriggered = 0;
    
    writeValues[0] = 0;
    writeValues[1] = 0;

    chanAStates[0] = 0;
    chanAStates[1] = 0;
    chanAStates[2] = 0;
    chanAStates[3] = 0;


    chanBStates[0] = 0;
    chanBStates[1] = 0;
    chanBStates[2] = 0;
    chanBStates[3] = 0;

    counterAStates[0] = 0;
    counterAStates[1] = 0;
    counterAStates[2] = 0;
    counterAStates[3] = 0;

    counterBStates[0] = 0;
    counterBStates[1] = 0;
    counterBStates[2] = 0;
    counterBStates[3] = 0;
    counterValues[0] = 0;
    counterValues[1] = 0;

  }



  // **********************************
  // STATE #1 is the init state.
  // **********************************
  else if (pyState == 1) {
    initArTime = millis();
  }

  else if (pyState == 2) {

    // always increment time and see if we are out of it
    tTime = tTime + 1;
    if (tTime <= trainDur) {
      pulsing = 1;

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


      writeValues[0] = pulseTrain(tTime, chanAStates, baselineA, nPulseA,
                                  delayTimeA, pulseTimeA, stimAmp_chanA);
      writeValues[1] = pulseTrain(tTime, chanBStates, baselineB, nPulseB,
                                  delayTimeB, pulseTimeB, stimAmp_chanB);
      counterValues[0] = pulseTrain(tTime, counterAStates, 0, -1, counterInts[0], 2, 1);
      counterValues[1] = pulseTrain(tTime, counterBStates, 0, -1, counterInts[1], 2, 1);

      analogWrites();
      digitalWrites();
      analogReads();

      spitData();
    }

    else if (tTime > trainDur) {
      pulsing = 0;
      analogWrites();
      analogReads();

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
  Serial.print(trainDur);
  Serial.print(',');
  Serial.print(counterInts[0]);
  Serial.print(',');
  Serial.println(counterInts[1]);

}


void spitData() {

  Serial.print("data");
  Serial.print(',');
  Serial.print(tTime);
  Serial.print(',');
  Serial.print(writeValues[0]);
  Serial.print(',');
  Serial.print(writeValues[1]);
  Serial.print(',');
  Serial.print(readValues[0]);
  Serial.print(',');
  Serial.print(readValues[1]);
  Serial.print(',');
  Serial.print(readValues[2]);
  Serial.print(',');
  Serial.print(readValues[3]);
  Serial.print(',');
  Serial.print(readValues[4]);
  Serial.print(',');
  Serial.print(counterValues[0]);
  Serial.print(',');
  Serial.print(millis() - initArTime);
  Serial.print(',');
  Serial.println(pulsing); // debug jank

}

bool flagReceive(char varAr[], int valAr[]) {
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
      for ( int i = 0; i < 14; i++) {
        if (rc == varAr[i]) {
          selectedVar = i;
          recvInProgress = true;
          Serial.println(selectedVar);
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
        valAr[selectedVar] = nVal;

      }
    }
  }
  return newData; // tells us if a valid variable arrived.
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
  counterInts[0]=knownValues[12];
  counterInts[1]=knownValues[13];

}

void resetVars() {
  for ( int i = 0; i < 14; i++) {
    knownValues[i] = -1;
  }
}

void analogReads() {
  for ( int i = 0; i < 6; i++) {
    readValues[i] = analogRead(adcChans[i]);
  }
}

void analogWrites() {
  for ( int i = 0; i < 2; i++) {
    analogWrite(dacChans[i], writeValues[i]);
  }
}

void digitalWrites() {
  for ( int i = 0; i < 2; i++) {
    digitalWrite(counterChans[i], counterValues[i]);
  }
}




// %%%%%%%%%% Pulse Train Function
int pulseTrain(float cTime, int chanStates[], int blDur,  int nPulse,
               int delayTime, int pulseTime, int stimAmp) {
  bool infPulse = 0;
  if (nPulse < 0) {
    infPulse = 1;
  }

  int writeVal = 0;

  // Chan State Map: baselineComp,inPulse,stateCounter,pulseCounter

  // ***** baseline state
  if (chanStates[0] == 0) {
    if (cTime <= blDur) {
      chanStates[1] = 0; // in pulse?
      chanStates[2] = 0; // state counter
    }

    else if (cTime > blDur) {
      chanStates[0] = 1; // baseline done
      chanStates[1] = 1; // in pulse
      chanStates[2] = 0; // but for 0th time.
      writeVal = stimAmp; // write the first value
    }
  }
  // ***** END baseline state

  // ***** Pulse State
  else if (chanStates[1] == 1) {

    if (chanStates[2] < pulseTime) {
      // starts at 0 and climbs to sample before pulseTime
      writeVal = stimAmp;
    }

    // exit condition
    else if (chanStates[2] >= pulseTime) {
      chanStates[1] = 0; // now in dwell state
      chanStates[2] = 0; // for the 0th time
      writeVal = 0;
    }
  }
  // ***** END Pulse State


  // ***** Dwell State
  else if (chanStates[1] == 0) {
    if (chanStates[2] < delayTime) {
      // starts at 0 and climbs to sample before delayTime
      writeVal = 0;
    }

    // exit condition
    else if (chanStates[2] >= delayTime) {
      chanStates[3] = chanStates[3] + 1; // increment the pulse counter

      if (chanStates[3] < nPulse || infPulse == 1) {
        chanStates[1] = 1; // now in pulse state
        chanStates[2] = 0; // for the 0th time
        writeVal = stimAmp;
      }

      else if (chanStates[3] >= nPulse) {
        chanStates[1] = 0; // stay in the dwell state
      }
    }
  }

  // Always increment state and write
  chanStates[2] = chanStates[2] + 1;
  return writeVal;
}
