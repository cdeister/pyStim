# pyStim

A simple python/teensy script combo that enables trial-based hardware timed analog and digital I/O.

Current functionality is limited only by the lack of a user interface. However, in its infant state it can be used for two channel analog input/output (pulse train only for now) with a digital output trigger.

Channel A is DAC0 (A21)
Channel B is DAC1 (A22)
Analog Input Read for Channel A is (A9)
Analog Input Read for Channel B is (A8)
Digital Trigger Out (10 ms at stim onset) is (Pin 6)

