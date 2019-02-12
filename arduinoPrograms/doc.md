# motor.ino

## Background

A stepper motor operates by moving in small increments called steps.
Steps are completed in sequences of four, then repeated.
If one cycle is defined as four steps, then one revolution of the motor shaft will
require fifty cycles, or two-hundred steps.

## Code Structure

In *motor.ino* each revolution is broken down into fifty cycles. Each cycle is broken
down into four steps. Each step is broken down into the individual wires that must
be activated to complete said step.

## Features To Add

- Ability to specify a degree of rotation and have the motor shaft turned to
that degree.

  - Each step turns the motor shaft 1.80°.