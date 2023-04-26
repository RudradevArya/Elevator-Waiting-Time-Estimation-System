#include<Stepper.h>
#include <Wire.h> 
#include <LiquidCrystal_I2C.h>

/////INIT hardware part////
#define CALL_BUTTONS A1    //--------Here is connection buttons of colling elevator
#define FLOOR_SENSORS A0   //--------Here is connection sensors which are localed on floors
#define CALIBRATION_SENSOR 2 //------Here is connected button for instalation the elevator on first floor
///////////////////////////
#define DEFAULT_SPEED 300 // Default speed of elevator
#define SLOW_SPEED 150  // Default speed of elevator when it is landing
#define N 4 //Number of floor

////////Flags of moving the elevator//////////
#define MOVING_UP 1 //This flag means that the elevator is moving up
#define MOVING_DOWN -1 //This flag means that the elevator is moving down
#define NOT_MOVING 0
/////////////////////////////////////////////

#define NOT -1

///////COMANDS FOR PANEL_CONTROL ///////
#define ELEVATOR_IS_ERIVED 1

////////////////Init motor///////////////////////
unsigned short stepsPerRevolution = 200;
Stepper myStepper(stepsPerRevolution, 8,9,10,11); // Conected Step motor
/////////////////////////////////////////////////

LiquidCrystal_I2C lcd(0x27,16,2);//Connected LDC display

short registeredFloor;
short arrayFloor[N] = {-1,-1,-1,-1};
short ledFloor[N] = {7,6,5,4};
short executableFloor = NOT; // -1 it means not called floors
boolean canWork = true;
boolean landed = false;
boolean waitForNext = true;
short flagMoving = NOT_MOVING;
short calledFloorFromCabine = NOT;


boolean flagPressSameBtn = true;

void setup() {
   Serial.begin(750);
  pinMode(CALL_BUTTONS,INPUT);
  pinMode(FLOOR_SENSORS,INPUT);
  pinMode(CALIBRATION_SENSOR, INPUT);
  
  for(byte i = 0; i < N; i++)
    pinMode(ledFloor[i],OUTPUT);
  
  myStepper.setSpeed(DEFAULT_SPEED);

  lcd.begin();                            
  lcd.backlight();                     
  printInf();
  calibration();
}
void loop() 
{
  //readComFromPanelControl();   
  
  registerFloor();
  writeTurn();

  if(waitForNext && canWork)
    nextFloor(); 
 
  if(executableFloor != NOT && canWork)
    moveElevator();
    
  delay(1);
}

void nextFloor()
{ 
  
  if(calledFloorFromCabine != NOT && calledFloorFromCabine != registeredFloor )
  {
    executableFloor = calledFloorFromCabine;
    landed = false;
    waitForNext = false;
    return;
  }

  if(arrayFloor[0] == NOT)
  {
    for(byte i = 0; i < N; i++)
    {
      swipeArray(arrayFloor);
      if(arrayFloor[0] != NOT)
        break;
    }
  }
    executableFloor = arrayFloor[0];

    if(executableFloor != NOT)
    {
      swipeArray(arrayFloor);
      landed = false;
      waitForNext = false;
    }

}

void swipeArray(short * arrayFloor){
  for(byte i = 0; i < N - 1; i++)
    arrayFloor[i] = arrayFloor[i+1];
  arrayFloor[N-1] = NOT;  
}

void moveElevator()
{

   if(executableFloor == registeredFloor && !landed)
  {
    if(flagMoving == MOVING_UP)
      moveUpMiddle();
    else if(flagMoving == MOVING_DOWN)
       moveDownMiddle();
       
    ElevatorArrived(executableFloor);
    return;    
  }
    
  if(executableFloor > registeredFloor)
  {
    moveUp();
    flagMoving = MOVING_UP;
  }else if(executableFloor < registeredFloor)
  {
    moveDown();
    flagMoving = MOVING_DOWN;
  }
}

void ElevatorArrived(short ArrivedOnFloor)
{

  for(byte i = 0; i < N; i++)
    if(arrayFloor[i] == ArrivedOnFloor)
        arrayFloor[i] = NOT;

  executableFloor = NOT;
  turnOffLedOnFloor(ArrivedOnFloor);
  sendCommandToPanelControl(ELEVATOR_IS_ERIVED);
  flagMoving = NOT_MOVING;
  waitForNext = true;
  
  if(calledFloorFromCabine == registeredFloor)
    calledFloorFromCabine = NOT;
    
  landed = true;
  canWork = false;
}

void turnOffLedOnFloor(short ArrivedOnFloor)
{
  digitalWrite(ledFloor[ArrivedOnFloor-1],LOW);
}

void writeTurn()
{ 
  short localCalledFloorExpected = calledFloor(); //called buttons
 
  ///////if we call the elevator on floor wheme we are, elevator will just send command to the cabin for opening door
  if( (localCalledFloorExpected == registeredFloor && flagPressSameBtn && executableFloor == NOT) || 
      (calledFloorFromCabine == registeredFloor && executableFloor == NOT && flagPressSameBtn ))
  {
    digitalWrite(ledFloor[localCalledFloorExpected - 1],HIGH);
    delay(10);
    digitalWrite(ledFloor[localCalledFloorExpected - 1],LOW);
    sendCommandToPanelControl(ELEVATOR_IS_ERIVED);
    calledFloorFromCabine = NOT;
    flagPressSameBtn = false;
    return;
  }

  ///here we create queue calling the elevator
  if(localCalledFloorExpected != NOT)
  {
    if(executableFloor == NOT && localCalledFloorExpected == registeredFloor)
      return;

    //if called floor is in queue, it will not add to queue again
    for (byte i = 0; i < 4;i++)
      if (localCalledFloorExpected == arrayFloor[i])
          return;
          
      for (byte i = 0; i < 4; i++)
        if (arrayFloor[i] == -1)
        {
          arrayFloor[i] = localCalledFloorExpected;
          digitalWrite(ledFloor[abs(localCalledFloorExpected)-1],HIGH);// Turn on led on floor which called
          return;
        }
  }
}

void calibration()
{
  for (byte i = 0; i < N; i++)
    digitalWrite(ledFloor[i], HIGH);
  lcd.setCursor(0,0); 
  lcd.print("  CALIBRATION...");
  
  while(!digitalRead(CALIBRATION_SENSOR))
    myStepper.step(-10);
    
  for (byte i = 0; i < N; i++)
    digitalWrite(ledFloor[i], LOW);
    
  registeredFloor = 1;  
  lcd.clear();
  lcd.print("Floor:1");
}

void moveUp()
{
  Serial.println(1);
  myStepper.step(50);
}

void moveUpMiddle()
{
  Serial.println(1);
  myStepper.setSpeed(SLOW_SPEED);

  switch(registeredFloor)
  {
    case 2:
      myStepper.step(950);
      break;
    case 3:
      myStepper.step(900);
      break;
    case 4:
      myStepper.step(900);
      break;
  }
  myStepper.setSpeed(DEFAULT_SPEED);
}

void moveDownMiddle()
{
  Serial.println(0);
  myStepper.setSpeed(SLOW_SPEED);
  switch(registeredFloor)
  {
    case 1:
      myStepper.step(-700);
      break;
    case 2:
      myStepper.step(-950);
      break;
    case 3:
      myStepper.step(-950);
      break;
    case 4:
      myStepper.step(-650);
      break;
  }
  myStepper.setSpeed(DEFAULT_SPEED);
}

void moveDown()
{
  Serial.println(0);
  myStepper.step(-50);
}

void registerFloor()
{
  unsigned short value = analogRead(FLOOR_SENSORS);
  short bufRegisteredFloor = 0;
  if(value >= 930 && value <= 935)
  {
    Serial.println(value);
    bufRegisteredFloor = 4;
  } 
  else if(value >= 890 && value <= 900) 
  {
    Serial.println(value);  
    bufRegisteredFloor = 3;
  }
  else if(value >= 845 && value <= 850)
  {
    Serial.println(value);
    bufRegisteredFloor = 2;
  } 
  else if(value >= 780 && value <= 790)
  {
    Serial.println(value);
    bufRegisteredFloor = 1;
  } 
  
  if(bufRegisteredFloor != 0 && bufRegisteredFloor != registeredFloor)
  {
    registeredFloor = bufRegisteredFloor;
    printFloor();
  }
}

short calledFloor()
{
  short value = analogRead(CALL_BUTTONS);

  if(value >= 860 && value <= 875)
  {
    Serial.println(value);
    return 4;
  }  
  else if(value >= 950 && value <= 965) 
  {
    Serial.println(value);
    return 3;
  } 
  else if(value >= 975 && value <= 982) 
  {
    Serial.println(value);
    return 3;
  } 
  else if(value >= 988 && value <= 998)
  {
    Serial.println(value);
    return 2; 
  } 
  else if(value >= 1002 && value <= 1009) 
  {
    Serial.println(value);
    return 2; 
  }  
  else if(value >= 1018 && value <= 1023)
  {
    Serial.println(value);
    return 1;
  }  
  else return NOT;
  
}

void printFloor()
{
  lcd.clear();
  lcd.setCursor(0,0);
  lcd.print("Floor:");
  lcd.print(registeredFloor);
}

void printInf()
{
  lcd.print("    Elevator");
  lcd.setCursor(0,1);
  lcd.print("Mini Project");
  delay(3000);
  //lcd.setCursor(0,1);
  //lcd.println("S.Michalewski   ");
  //delay(2000);
  lcd.clear();
}

void sendCommandToPanelControl(short command)
{
  char str[2] = {'0','0'};
  switch(command)
  {
    case ELEVATOR_IS_ERIVED:
      str[0] = 'e';
      str[1] = 'f';
        break;    
  }

  Serial.write(str,2);
}

void readComFromPanelControl()
{
  if(!Serial.available())
    return;

    byte i = 0;
    char str[2] = {'0','0'};
    delay(100);
    while(Serial.available())
      str[i++] = Serial.read();  

   if(str[0] == 'd' && str[1] == 'o')
    canWork = false;
   else if(str[0] == 'd' && str[1] == 'c')
   {
    canWork = true;
    flagPressSameBtn = true;
   }else if(str[0] == 'c')
   {
      calledFloorFromCabine = str[1] - '0';
   }
}