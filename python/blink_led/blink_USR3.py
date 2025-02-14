"""
--------------------------------------------------------------------------
Blinking Leds
--------------------------------------------------------------------------
License: Justin Cooper, Adafruit Industries. BeagleBone IO Python library is released under the MIT License.  
Copyright 2025 - <Mert Culcu>

Redistribution and use in source and binary forms, with or without 
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, 
this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice, 
this list of conditions and the following disclaimer in the documentation 
and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its contributors 
may be used to endorse or promote products derived from this software without 
specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE 
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE 
ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE 
LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR 
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF 
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS 
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN 
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) 
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF 
THE POSSIBILITY OF SUCH DAMAGE.
--------------------------------------------------------------------------
"""

import Adafruit_BBIO.GPIO as GPIO
import time

user3_led = "USR3"
frequency = 5  
period = 1.0 / frequency  
duty_cycle = 0.5  
on_time = period * duty_cycle
off_time = period * (1 - duty_cycle)

GPIO.setup(user3_led, GPIO.OUT)

def blink():
    try:
        while True:
            GPIO.output(user3_led, GPIO.HIGH)  # Turn LED on
            time.sleep(on_time)
            GPIO.output(user3_led, GPIO.LOW)   # Turn LED off
            time.sleep(off_time)

def main():
    blink()

if __name__ == "__main__":
    main()