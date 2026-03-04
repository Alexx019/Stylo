#include <Wire.h>

const int MPU_ADDR = 0x68; // Dirección I2C por defecto del MPU6050
const int pressurePin = 4; 
const int threshold = -1;

void setup() {
  Serial.begin(115200);
  Wire.begin(21, 22); // SDA, SCL específicos de la ESP32

  // 1. Despertar al MPU6050 (por defecto viene en modo "sleep")
  Wire.beginTransmission(MPU_ADDR);
  Wire.write(0x6B); // Registro PWR_MGMT_1
  Wire.write(0);    // Poner a 0 para despertarlo
  if (Wire.endTransmission() != 0) {
    Serial.println("¡Error! No se encuentra el sensor en 0x68. Revisa cables.");
    while(1);
  }
  
  // Serial.println("ax,ay,az,gx,gy,gz,p");
}

void loop() {
  int pressureValue = analogRead(pressurePin);
  bool impSep = false;

  if (pressureValue > threshold) {
    impSep = true;
    // 2. Pedir los 14 registros de datos (Acc, Temp, Gyro)
    Wire.beginTransmission(MPU_ADDR);
    Wire.write(0x3B); // Empezar en el registro del Acelerómetro X
    Wire.endTransmission(false);
    Wire.requestFrom(MPU_ADDR, 14, true);

    // 3. Leer y combinar bytes (cada valor son 2 bytes: High y Low)
    int16_t ax = Wire.read() << 8 | Wire.read();
    int16_t ay = Wire.read() << 8 | Wire.read();
    int16_t az = Wire.read() << 8 | Wire.read();
    int16_t temp = Wire.read() << 8 | Wire.read(); // Ignoramos temperatura
    int16_t gx = Wire.read() << 8 | Wire.read();
    int16_t gy = Wire.read() << 8 | Wire.read();
    int16_t gz = Wire.read() << 8 | Wire.read();

    // Imprimir en CSV
    Serial.print(ax); Serial.print(",");
    Serial.print(ay); Serial.print(",");
    Serial.print(az); Serial.print(",");
    Serial.print(gx); Serial.print(",");
    Serial.print(gy); Serial.print(",");
    Serial.print(gz); Serial.print(",");
    Serial.println(pressureValue);
  }
  
  delay(20); // Muestreo estable
}