// using namespace std;

int pin1 = 7;
int pin2 = 8;
int pin3 = 6;
int pin4 = 5;
int step_delay = 20;


void forward_step_1() {
  // Perform the 1st step necessary.
digitalWrite(pin1, LOW);
digitalWrite(pin2, LOW);
digitalWrite(pin3, HIGH);
digitalWrite(pin4, HIGH);
}

void forward_step_2() {
  // Perform the 2nd step necessary.
digitalWrite(pin1, LOW);
digitalWrite(pin2, HIGH);
digitalWrite(pin3, HIGH);
digitalWrite(pin4, LOW);
}

void forward_step_3() {
  // Perform the 3rd step necessary.
digitalWrite(pin1, HIGH);
digitalWrite(pin2, HIGH);
digitalWrite(pin3, LOW);
digitalWrite(pin4, LOW);
}

void forward_step_4() {
  // Perform the 4th step necessary.
digitalWrite(pin1, HIGH);
digitalWrite(pin2, LOW);
digitalWrite(pin3, LOW);
digitalWrite(pin4, HIGH);
}

// Begin code for running backwards.
void backward_step_1() {
  // Perform the 1st step necessary.
digitalWrite(pin1, HIGH);
digitalWrite(pin2, LOW);
digitalWrite(pin3, HIGH);
digitalWrite(pin4, LOW);
}

void backward_step_2() {
  // Perform the 2nd step necessary.
digitalWrite(pin1, LOW);
digitalWrite(pin2, HIGH);
digitalWrite(pin3, HIGH);
digitalWrite(pin4, LOW);
}

void backward_step_3() {
  // Perform the 3rd step necessary.
digitalWrite(pin1, LOW);
digitalWrite(pin2, HIGH);
digitalWrite(pin3, LOW);
digitalWrite(pin4, HIGH);
}

void backward_step_4() {
  // Perform the 4th step necessary.
digitalWrite(pin1, HIGH);
digitalWrite(pin2, LOW);
digitalWrite(pin3, LOW);
digitalWrite(pin4, HIGH);
}

void cycle_forward(int ms_delay) {
  // perform each step with desired delay, delay affecting speed of motor.
  forward_step_1();
  delay(ms_delay);
  forward_step_2();
  delay(ms_delay);
  forward_step_3();
  delay(ms_delay);
  forward_step_4();
  delay(ms_delay);
}

void cycle_backward(int ms_delay) {
  // perform each step with desired delay, delay affecting speed of motor.
  backward_step_1();
  delay(ms_delay);
  backward_step_2();
  delay(ms_delay);
  backward_step_3();
  delay(ms_delay);
  backward_step_4();
  delay(ms_delay);
}

void one_forward_revolution() {
  // The 12V motors used have a 200 step per revolution ratio.
  // If one cycle is 4 steps, one revolution will require 50 cycles.
  for (int cycle = 0; cycle <= 50; cycle++) {
    cycle_forward(step_delay);
  }
}

void one_backward_revolution() {
  // For explanation, see one_forward_revolution above.
  for (int cycle = 0; cycle <= 50; cycle++) {
    cycle_backward(step_delay);
  }
}

void setup() {
pinMode(pin1, OUTPUT);
pinMode(pin2, OUTPUT);
pinMode(pin3,OUTPUT);
pinMode(pin4,OUTPUT);
}

void loop() {
  one_forward_revolution();
  one_backward_revolution();
}