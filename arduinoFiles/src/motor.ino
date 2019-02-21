// in1, ..., in4 refers to the "in" pins on the L298N motor driver used for 
// the stepper motors.
int in1 = 1;
int in2 = 2;
int in3 = 3;
int in4 = 4;
int step_delay = 20;  // Delay between each step.

void forward_step_1()
{ // Perform the 1st step necessary for rotating forwards.
  digitalWrite(in1, LOW);
  digitalWrite(in2, LOW);
  digitalWrite(in3, HIGH);
  digitalWrite(in4, HIGH);
}

void backward_step_1()
{ // Perform the 1st step necessary for rotating backwards.
  digitalWrite(in1, HIGH);
  digitalWrite(in2, LOW);
  digitalWrite(in3, HIGH);
  digitalWrite(in4, LOW);
}

void step_2()
{ // Perform the 2nd step necessary for rotating forwards or backwards.
  digitalWrite(in1, LOW);
  digitalWrite(in2, HIGH);
  digitalWrite(in3, HIGH);
  digitalWrite(in4, LOW);
}

void forward_step_3()
{ // Perform the 3rd step necessary for rotating forwards.
  digitalWrite(in1, HIGH);
  digitalWrite(in2, HIGH);
  digitalWrite(in3, LOW);
  digitalWrite(in4, LOW);
}

void backward_step_3()
{ // Perform the 3rd step necessary for rotating backwards.
  digitalWrite(in1, LOW);
  digitalWrite(in2, HIGH);
  digitalWrite(in3, LOW);
  digitalWrite(in4, HIGH);
}

void step_4()
{ // Perform the 4th step necessary for rotating forwards or backwards.
  digitalWrite(in1, HIGH);
  digitalWrite(in2, LOW);
  digitalWrite(in3, LOW);
  digitalWrite(in4, HIGH);
}

void cycle_forward(int ms_delay)
{ // Perform each step with desired delay.
  // The ms_delay variable is passed in when the function is called.
  forward_step_1();
  delay(ms_delay);
  step_2();
  delay(ms_delay);
  forward_step_3();
  delay(ms_delay);
  step_4();
  delay(ms_delay);
}

void cycle_backward(int ms_delay)
{ // Perform each step with desired delay.
  // The ms_delay variable is passed in when the function is called.
  backward_step_1();
  delay(ms_delay);
  step_2();
  delay(ms_delay);
  backward_step_3();
  delay(ms_delay);
  step_4();
  delay(ms_delay);
}

void one_forward_revolution()
{ // Rotate 360° forward. 
  for (int cycle = 0; cycle <= 50; cycle++)
  { // Perform 50 cycles forward.
    cycle_forward(step_delay);
  }
}

void one_backward_revolution()
{ // Rotate 360° backward.
  for (int cycle = 0; cycle <= 50; cycle++)
  { // Perform 50 cycles backwards.
    cycle_backward(step_delay);
  }
}

void setup()
{ // Set pins to accept input or output.
  pinMode(in1, OUTPUT);
  pinMode(in2, OUTPUT);
  pinMode(in3, OUTPUT);
  pinMode(in4, OUTPUT);
}

void loop()
{
  one_forward_revolution();
  one_backward_revolution();
}