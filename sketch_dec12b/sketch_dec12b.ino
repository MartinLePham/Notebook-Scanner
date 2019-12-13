#include <Stepper.h>

char serialData;
char serialStart;
char serialSpeed;
char serialEdge;
char serialMid;
char serial_x;
char serial_y;

//laptop dimension variables
//int array_length = 10;
float edges_x[10];
float edges_y[10];
int cnt_x = 0; // counters for array appending
int cnt_y = 0;
int edge = 0;

int top_left = 0;
int middle_screen = 0;

//camera position variables
int current_position_x = 0;
int current_position_y = 0;
int x_limit = 3000;
int y_limit = 280;
const int position_y_from_home = 255; // about 290mm down from home

//camera speed variables
   // motor step angle = 1.8 degrees
   // 200 steps/rev = 1 rotation
   // Distance (steps/mm) = steps_per_revolution * leadscrew
    // 1600 steps/mm = 200 * 8 rev/mm -- for 1 mm of travel
int motor_speed_x = 2000;
int motor_speed_y = 2000;
int steps_per_revolution = 200; // equals 1/8 mm of travel

//initialize stepper motors and limit switches
Stepper myStepper_x(steps_per_revolution, 8, 9);
Stepper myStepper_y(steps_per_revolution, 10, 11);
const int Limit_Switch_X = 5;
const int Limit_Switch_Y = 6;
const int Precision_Switch = 7;

int wait = 1000;

void setup() {
  pinMode(Limit_Switch_X, INPUT);
  pinMode(Limit_Switch_Y, INPUT);
  pinMode(Precision_Switch, INPUT);
  Serial.begin(115200);
  Serial.setTimeout(5);
}

void tellPython() {
  Serial.flush();
  Serial.write('b');
}

void loop() {
  while(!Serial.available()){}
  String buff = Serial.readString();
  Serial.print(buff);

  switch (buff[0])
  {
    case 'l': 
    {
        int steps = buff.substring(1).toInt();
        step_motor_left(steps);
        tellPython();
        break; 
    }
    case 'r':
    {
        int steps = buff.substring(1).toInt();
        step_motor_right(steps);
        tellPython();
        break;
    }
    case 'd':
    {
        int steps = buff.substring(1).toInt();
        step_motor_down(steps);
        tellPython();
        break;
    }
    case 'u':
    {
        int steps = buff.substring(1).toInt();
        step_motor_up(steps);
        tellPython();
        break;
    }
    case 'h':
    {
        go_home();
        tellPython();
        break;
    }
    default:
        tellPython();
        break;
  }
  
}//end of loop


// motion functions (facing the motion assembly) // at 1/8mm per function call
void step_motor_left(int steps) {
  myStepper_x.setSpeed(motor_speed_x);
  myStepper_x.step(steps);
  //delay(wait);
  current_position_x -= 1;
  //current_position_x -= (1/8)/(steps_per_revolution);
  
}

void step_motor_right(int steps) {
  myStepper_x.setSpeed(motor_speed_x);
  myStepper_x.step(-steps);  Serial.flush();

  //delay(wait);
  current_position_x += 1;
}

void step_motor_right_slow() {
  // check for edge
  myStepper_x.setSpeed(motor_speed_x);
  myStepper_x.step(-steps_per_revolution);
  //delay(wait);
  current_position_x += 1/2;
}

void step_motor_up(int steps) {
  myStepper_y.setSpeed(motor_speed_y);
  myStepper_y.step(-steps);
  //delay(wait);
  current_position_y -= 1;
}

void step_motor_down(int steps) {
  myStepper_y.setSpeed(motor_speed_y);
  myStepper_y.step(steps);
  //delay(wait);
  current_position_y += 1;
}

void step_motor_down_slow() {
  myStepper_y.setSpeed(motor_speed_y/8);
  myStepper_y.step(steps_per_revolution);
  //delay(wait);
  current_position_y += 1/2;
}

void go_home() {
  if (digitalRead(Limit_Switch_X) == LOW && digitalRead(Limit_Switch_Y) == LOW){
    current_position_x = 0;
    current_position_y = 0;
  }
  else {
    while (digitalRead(Limit_Switch_X) == HIGH) {
      step_motor_left(200);
    }
    while (digitalRead(Limit_Switch_Y) == HIGH) {
      step_motor_up(200);
    }
  }
  current_position_x = 0;
  current_position_y = 0;
}
