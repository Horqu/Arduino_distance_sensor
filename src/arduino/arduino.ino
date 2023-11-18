#include <LiquidCrystal.h>

const uint8_t TRIGER_PIN = 13;
const uint8_t ECHO_PIN = 12;
const uint8_t BUZZER_PIN = 11;
const uint8_t LCD_RS_PIN = 10;
const uint8_t LCD_E_PIN = 9;

const uint8_t LCD_D4_PIN = 4;
const uint8_t LCD_D5_PIN = 5;
const uint8_t LCD_D6_PIN = 6;
const uint8_t LCD_D7_PIN = 7;

const LiquidCrystal LCD(LCD_RS_PIN, LCD_E_PIN, LCD_D4_PIN, LCD_D5_PIN, LCD_D6_PIN, LCD_D7_PIN);

const float DEFAULT_CLOSE_DISTANCE = 10.0f;
const float DEFAULT_FAR_DISTANCE = 50.0f;

float close_distance = DEFAULT_CLOSE_DISTANCE;
float far_distance = DEFAULT_FAR_DISTANCE;

unsigned long duration_micro_sec;
float distance_in_cm;

/**
 * The function takes as value the time in micro seconds that the sound wave traveled on the path: sensor -> object -> sensor
 * And returns distance between sensor and object
 *
 * @param duration_in_micro_sec
 * @return distance between sensor and object in cm
**/
float calculateDistanceInCm(unsigned long duration_in_micro_sec) {
    return 0.017 * duration_in_micro_sec;
}

void setup() {
    Serial.begin(9600);

    LCD.begin(16, 2);

    LCD.print("Loading...");

    pinMode(TRIGER_PIN, OUTPUT);

    pinMode(ECHO_PIN, INPUT);

    pinMode(BUZZER_PIN, OUTPUT);
}

void loop() {
  
    digitalWrite(TRIGER_PIN, HIGH);
    delayMicroseconds(10);
    digitalWrite(TRIGER_PIN, LOW);
   
    duration_micro_sec = pulseIn(ECHO_PIN, HIGH);
    distance_in_cm = calculateDistanceInCm(duration_micro_sec);

    LCD.clear();
    LCD.setCursor(0, 0);
    LCD.print("Distance: ");

    LCD.setCursor(0, 1);
    LCD.print("    ");
    LCD.print(distance_in_cm);
    LCD.print(" cm.");

    if (Serial.available() > 0) {

      String data = Serial.readStringUntil('\n');
      int comma_index = data.indexOf(',');

      String close_dist_value_string = data.substring(0, comma_index);
      close_distance = close_dist_value_string.toFloat();

      String far_dist_value_string = data.substring(comma_index + 1);
      far_distance = far_dist_value_string.toFloat();

    }

    if (distance_in_cm < close_distance) {
        for (int i = 0; i < 4; i++) {
            digitalWrite(BUZZER_PIN, HIGH);
            delay(125);
            digitalWrite(BUZZER_PIN, LOW);
            delay(125);
        }
    } else if (distance_in_cm < far_distance) {
        for (int i = 0; i < 2; i++) {
            digitalWrite(BUZZER_PIN, HIGH);
            delay(250);
            digitalWrite(BUZZER_PIN, LOW);
            delay(250);
        }
    } else {
        digitalWrite(BUZZER_PIN, HIGH);
        delay(500);
        digitalWrite(BUZZER_PIN, LOW);
        delay(500);
    }

}
