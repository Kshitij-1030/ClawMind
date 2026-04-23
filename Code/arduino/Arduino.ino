const int STEP = 3;
const int DIR = 2;

const int ENA_X = 9;
const int IN1_X = 8;
const int IN2_X = 7;

const int ENA_C = 10;
const int IN1_C = 11;
const int IN2_C = 12;

const int LIMIT_Y_A = A4;
const int LIMIT_Y_B = A3;

String command = "";

void stopAll() {
  digitalWrite(IN1_X, LOW); digitalWrite(IN2_X, LOW);
  digitalWrite(IN1_C, LOW); digitalWrite(IN2_C, LOW);
}

void stepMotor(bool forward) {
  if (forward && digitalRead(LIMIT_Y_A) == LOW) return;
  if (!forward && digitalRead(LIMIT_Y_B) == LOW) return;
  digitalWrite(DIR, forward ? HIGH : LOW);
  digitalWrite(STEP, HIGH);
  delayMicroseconds(1500);
  digitalWrite(STEP, LOW);
  delayMicroseconds(1500);
}

void setup() {
  Serial.begin(9600);
  pinMode(STEP, OUTPUT);
  pinMode(DIR, OUTPUT);
  pinMode(ENA_X, OUTPUT);
  pinMode(IN1_X, OUTPUT);
  pinMode(IN2_X, OUTPUT);
  pinMode(ENA_C, OUTPUT);
  pinMode(IN1_C, OUTPUT);
  pinMode(IN2_C, OUTPUT);
  pinMode(LIMIT_Y_A, INPUT_PULLUP);
  pinMode(LIMIT_Y_B, INPUT_PULLUP);
  analogWrite(ENA_X, 120);
  analogWrite(ENA_C, 60);
  stopAll();
  Serial.println("Arduino ready");
}

void loop() {
  if (Serial.available()) {
    command = Serial.readStringUntil('\n');
    command.trim();
  }

  // Look left → move right, look right → move left (swapped)
  if (command == "X+") {
    stepMotor(true);   // swapped
  }
  else if (command == "X-") {
    stepMotor(false);  // swapped
  }
  else if (command == "Y+") {
    digitalWrite(IN1_X, LOW); digitalWrite(IN2_X, HIGH);
  }
  else if (command == "Y-") {
    digitalWrite(IN1_X, HIGH); digitalWrite(IN2_X, LOW);
  }
  else if (command == "GO") {
    digitalWrite(IN1_C, HIGH); digitalWrite(IN2_C, LOW);
  }
  else if (command == "OP") {
    digitalWrite(IN1_C, LOW); digitalWrite(IN2_C, HIGH);
  }
  else if (command == "ST") {
    stopAll();
  }

  if (command == "X+" || command == "X-") {
    stepMotor(command == "X+");  // swapped
  }
}