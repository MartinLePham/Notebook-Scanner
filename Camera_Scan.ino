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
  Serial.begin(9600);
}

void loop() {
  
  // ---- *PYTHON TELLS ARDUINO TO START* ----
  serialStart = Serial.read();
  if (serialStart == 'G') {
    //Reset Home Position
    //Serial.println("Hi Python");
    go_home();
    
    //move camera down from home
    while (current_position_y < position_y_from_home) {
      step_motor_down();
//      Serial.println(current_position_y);
    }

    // ---- *PYTHON START IMAGING* ----
    delay(wait);
    Serial.println("Scan");
    delay(wait);
  
    //scan camera to the right
    while (current_position_x < x_limit) {
      serial_x = Serial.read(); // determine speed      
      if (serial_x == 'F') { // ----- *PYTHON FOUND EDGE AT PIXEL* ----
        myStepper_x.step(0);
        edge = current_position_x;  //read distance data 
        Serial.println(edge); // ----- *SEND EDGE POSITION TO PYTHON* ------
        edges_x[cnt_x] = edge; // for arduino purposes only
        cnt_x++;
//        delay(wait);/
      }
      if (serial_x == 'S') { // ---- *PYTHON DETECTED EDGE IN VIDEO* ----
        step_motor_right_slow();    
      }
      else {
        step_motor_right();
      }
    }
    
    //tell python to stop scanning and calculate middle
    delay(wait);
    Serial.println("x_limit");
    delay(wait); // allow python to read stop signal

    //move camera to middle of screen
    serialMid = Serial.parseFloat();
    //serialMid = 10; 
    while (current_position_x > serialMid) {
      step_motor_left();
    }
  
    //move camera to top
    while (current_position_y > 0) {
      step_motor_up();
    }

    //start Y scan
    delay(wait);
    Serial.println("StartY");
    delay(wait); // allow python code to loop again to start scan y
  
    //scan camera down
   // while (digitalRead(Precision_Switch) == LOW) {
    while (current_position_y < y_limit) {
      serial_y = Serial.read(); // determine speed
      if (serialEdge == 'F') { // ----- *PYTHON FOUND EDGE AT PIXEL* ----
        myStepper_y.step(0);
        edge = current_position_y;  //read distance data 
        Serial.println(edge); // ----- *SEND EDGE POSITION TO PYTHON* ------
        edges_y[cnt_y] = edge; // for arduino purposes only
        cnt_y++;
        delay(wait);
      }        
      if (serial_y == 'S') { // ---- *PYTHON DETECTED EDGE IN VIDEO* ----
        step_motor_down_slow();
      }
      else {
        step_motor_down();
      }
    }

    //bottomed Out, stop scanning
    delay(wait);
    Serial.println("StopY");
    delay(wait); //allow python to read stop signal

    // go to Top-Left
    while (current_position_x < edges_x[cnt_x]){
      step_motor_right();
    }
    while (current_position_y > edges_y[0])
    {
      step_motor_up();
    }

    // ---- TELL PYTHON TO TAKE PIC -----
    delay(wait);
    Serial.println("pic");
    delay(wait);    
    
    //go to Top-Right
//    Serial.println(edges_y[0]);
//    Serial.println(edges_x[0]);
    while (current_position_x > edges_x[0]){
      step_motor_left();
    }
    while (current_position_y > edges_y[0]){
      step_motor_up();
    }
     
    // ---- TELL PYTHON TO TAKE PIC -----
    delay(wait);
    Serial.println("pic");
    delay(wait);

    //return Home
      go_home();
   }
}//end of loop


// motion functions (facing the motion assembly) // at 1/8mm per function call
void step_motor_left() {
  myStepper_x.setSpeed(motor_speed_x);
  myStepper_x.step(steps_per_revolution);
  //delay(wait);
  current_position_x -= 1;
  //current_position_x -= (1/8)/(steps_per_revolution);
  
}

void step_motor_right() {
  myStepper_x.setSpeed(motor_speed_x);
  myStepper_x.step(-steps_per_revolution);
  //delay(wait);
  current_position_x += 1;
}

void step_motor_right_slow() {
  // check for edge
  myStepper_x.setSpeed(motor_speed_x/8);
  myStepper_x.step(-steps_per_revolution);
  //delay(wait);
  current_position_x += 1/2;
}

void step_motor_up() {
  myStepper_y.setSpeed(motor_speed_y);
  myStepper_y.step(-steps_per_revolution);
  //delay(wait);
  current_position_y -= 1;
}

void step_motor_down() {
  myStepper_y.setSpeed(motor_speed_y);
  myStepper_y.step(steps_per_revolution);
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
      step_motor_left();
    }
    while (digitalRead(Limit_Switch_Y) == HIGH) {
      step_motor_up();
    }
  }
  current_position_x = 0;
  current_position_y = 0;
}
