#include <PubSubClient.h>
#include <ESP8266WiFi.h>
//#include <WiFiClient.h>
//#include <ArduinoOTA.h>
//#include <WiFiUdp.h>
//#include <NTPClient.h>
//#include <ESP8266mDNS.h>
//#include <ESP8266WebServer.h>

#ifndef STASSID
#define STASSID "NUTHOUSE_2.4"
#define STAPSK  "pmwpmwpmw"
#define MQTTHOST "10.0.0.69"
#define MQTTPORT 1883
#define SLEEPTIME 10e6 //10 secs
#define SETTEMP 15
#endif

//struct to store connection info
 struct {
  uint32_t crc32;   // 4 bytes
  uint8_t channel;  // 1 byte,   5 in total
  uint8_t ap_mac[6];// 6 bytes, 11 in total
  uint8_t padding;  // 1 byte,  12 in total
} rtcData;

//Static IP
IPAddress ip(10, 0, 0, 96);
IPAddress gateway(10, 0, 0, 1);
IPAddress subnet(255, 255, 255, 0);
IPAddress dns(64, 59, 135, 148);

//Temp Sensor interrupt
void ICACHE_RAM_ATTR pulseDetect();
volatile unsigned int pulseCount = 0;

//WIFI
const char* ssid = STASSID;
const char* password = STAPSK;
bool rtcValid;

//MQTT stuff
const char* mqttServer = MQTTHOST;
const int mqttPort = MQTTPORT;
const char* mqttUser = NULL;
const char* mqttPassword = NULL;
const char* willTopic = "therm/STATUS";
const int willQoS = 0;
boolean willRetain = true;
const char* willMessage = "F";

//PINS
const int led = D2;
const int ssr = D6;
const int tempIn = D5;

//Global variables
boolean overrideIO = false;
boolean heating = false;
long sleepTime = SLEEPTIME;
float setTemp = SETTEMP;
float currentTemp;
unsigned int batt;

//For MQTT client
WiFiClient espClient;
PubSubClient client(espClient);


uint32_t calculateCRC32(const uint8_t *data, size_t length) {
  uint32_t crc = 0xffffffff;
  while (length--) {
    uint8_t c = *data++;
    for (uint32_t i = 0x80; i > 0; i >>= 1 ) {
      bool bit = crc & 0x80000000;
      if ( c & i ) {
        bit = !bit;
      }

      crc <<= 1;
      if ( bit ) {
        crc ^= 0x04c11db7;
      }
    }
  }
  return crc;
}

void ICACHE_RAM_ATTR pulseDetect() { //Pulse counter interrupt function
  pulseCount++;
}

void measureTemp() {//when called adds the reading to the array, once at the end it rewrites from the start
  attachInterrupt(digitalPinToInterrupt(tempIn), pulseDetect, FALLING);//using interrupt pin tp trigger on falling edge

  unsigned long conversionStartTime = millis();//keeps track of timing

  while (millis() - conversionStartTime < 10) { //looking for silence, in case we go to read temperature mid-measurement, ride it out till next one
    yield();//for the ESP8266 to keep other tasks happy
    if (pulseCount > 0) {
      pulseCount = 0;
      conversionStartTime = millis();
    }
  }

  pulseCount = 0;//reset pulse count
  while (millis() - conversionStartTime < 150) {//wait for first pulse
    yield();//for the ESP8266 to keep other tasks happy
    if (pulseCount > 0)
      break;
  }
  if (pulseCount == 0) {
    currentTemp = 1069.0;//FAIL - never got a pulse
    return;
  }

  conversionStartTime = millis();//conversion done, so reset time
  unsigned int oldPulseCount = pulseCount;//just to help keep track of timings when pulse pin goes idle
  unsigned long pulseTime = millis();
  while (millis() - conversionStartTime < 60) { //measure pulses
    yield();//for the ESP8266 to keep other tasks happy

    if (pulseCount != oldPulseCount) {//new pulse, so update timer
      oldPulseCount = pulseCount;
      pulseTime = millis();
    }
    else if (millis() - pulseTime > 5) {//no pulses for a while, must be done.
      break;
    }
  }
  //^^^ Stays stuck here counting pulese for 60ms

  if (pulseCount < 5) { //this is just noise, false trigger... I mean only 5 pulses, that can't be right
    currentTemp = 1420.0;//FAIL
    return;
  }

  detachInterrupt(digitalPinToInterrupt(tempIn));//done with the interrupt
  float temperatureC = 256.000 * pulseCount / 4096.000 - 50;//conversion
  //see 7.3.2 Output Transfer Function in Datasheet
  currentTemp = temperatureC;
}



//MQTT callback
void callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Message arrived in topic: ");
  Serial.println(topic);
  Serial.print("Message:");
  String message = "";
  for (int i = 0; i < length; i++) {
    //Serial.print((char)payload[i]);
    message += (char)payload[i];
  }
  message[length] = '\0';
  Serial.println(message);
    
  //Overriding
  if(strcmp(topic, "therm/OVERRIDE") == 0) {
    if( strncmp((char *)payload, "ON", length) == 0) {
      overrideIO = true;
      heating = true;
      digitalWrite(led, HIGH);
      digitalWrite(ssr, HIGH);
    }
    else if(strncmp((char *)payload, "OFF", length) == 0) {
      overrideIO = true;
      heating = false;
      digitalWrite(led, LOW);
      digitalWrite(ssr, LOW);
    }
    else if(strncmp((char *)payload, "CANCEL", length) == 0) {
      overrideIO = false;
    }
    else if(strncmp((char *)payload, "REBOOT", length) == 0) {
      ESP.reset();
    }
  }
      //Setting temperature
  if(strcmp(topic, "therm/TEMPSET") == 0) {
//    Serial.println("Setting new temp");
    setTemp = message.toFloat();
  }
}

//void connectWifi() {
//    WiFi.begin(ssid, password);
//    Serial.print("Connecting to WiFi Network: ");
//    Serial.print(ssid);
//    Serial.println(" ...");
//
//    int i = 0;
//    while (WiFi.status() != WL_CONNECTED) {
//      delay(1000);
//      Serial.print(++i); Serial.print(' ');
//      //light blinks every other second when connecting then goes hard on after connecting
//      if (i % 2 == 1) {
//        digitalWrite(led, HIGH);
//      }
//      else {
//        digitalWrite(led, LOW);
//      }
//    }
//    digitalWrite(led, LOW);
//      
//    Serial.println("\n");
//    Serial.print("Connection established in "); Serial.print(i); Serial.println(" seconds!");
//    Serial.print("IP address: ");
//    Serial.println(WiFi.localIP());
// }
void connectWiFi() {
    WiFi.forceSleepWake();
    delay(1);
    
    // Disable the WiFi persistence.  The ESP8266 will not load and save WiFi settings unnecessarily in the flash memory.
    WiFi.persistent(false);
    
    // Bring up the WiFi connection
    WiFi.mode(WIFI_STA);
    WiFi.config(ip, dns, gateway, subnet);
    //-----------Replacement for "WiFi.begin();" with a precedure using connection data stored by us
    if (rtcValid) {
      Serial.print("Connecting to WiFi Network: ");
      Serial.print(ssid);
      Serial.println(" with RTC info...");
      // The RTC data was good, make a quick connection
      WiFi.begin(ssid, password, rtcData.channel, rtcData.ap_mac, true );
    }
    else {
      Serial.print("Connecting to WiFi Network: ");
      Serial.print(ssid);
      Serial.println(" with RTC info...");
      // The RTC data was not valid, so make a regular connection
      WiFi.begin(ssid, password);
    }

    //------now wait for connection
    int retries = 0;
    int wifiStatus = WiFi.status();
    while (wifiStatus != WL_CONNECTED) {
      retries++;
      
      if ( retries == 100 ) {
        // Quick connect is not working, reset WiFi and try regular connection
        WiFi.disconnect();
        delay(10);
        WiFi.forceSleepBegin();
        delay(10);
        WiFi.forceSleepWake();
        delay(10);
        WiFi.begin(ssid, password);
        
      }
      if (retries == 600) {
        // Giving up after 30 seconds and going back to sleep
        WiFi.disconnect(true);
        delay(1);
        WiFi.mode(WIFI_OFF);
        ESP.deepSleep(SLEEPTIME, WAKE_RF_DISABLED );
        return; // Not expecting this to be called, the previous call will never return.
      }
      //light blinks every other second when connecting then goes hard on after connecting
      if (retries % 2 == 1) {
        digitalWrite(led, HIGH);
      }
      else {
        digitalWrite(led, LOW);
      }
      delay(50);
      wifiStatus = WiFi.status();
    }
  digitalWrite(led, LOW);
  
  //---------
  Serial.println("WiFi connected");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());

//   Write current connection info back to RTC
  rtcData.channel = WiFi.channel();
  memcpy( rtcData.ap_mac, WiFi.BSSID(), 6 ); // Copy 6 bytes of BSSID (AP's MAC address)
  rtcData.crc32 = calculateCRC32( ((uint8_t*)&rtcData) + 4, sizeof(rtcData) - 4 );
  ESP.rtcUserMemoryWrite( 0, (uint32_t*)&rtcData, sizeof(rtcData));
 }


void reconnectMQTT() {
//  Serial.println("reconnect MQTT called");
  String clientID = "ESP8266Client";
//  clientID += String(random(0xffff), HEX);
  while (!client.connected()) {
    if (client.connect(clientID.c_str(), mqttUser, mqttPassword, willTopic, willQoS, willRetain, willMessage)) {
      Serial.println("Connected to mqtt broker!");
    }
    else {
      Serial.print("mqtt broker connection failed with state: ");
      Serial.println(client.state());
      delay(2000);
    }
  }
  sendMQTTmessage("therm/main", "Welcome, the ESP8266 board is here.");
  client.publish("therm/STATUS", "TRUE", true);
  client.subscribe("therm/OVERRIDE");
  client.subscribe("therm/TEMPSET");
}

void sendDataRecord() {
  if(!client.connected()) {
    reconnectMQTT();
  }
  String toSend = String(currentTemp) + "/" + String(setTemp) + "/" + String(heating) + "/" + String(batt);
  const char* toSendChar = toSend.c_str();
  client.publish("therm/DATA", toSendChar);
  Serial.println("Data record sent!");
}

void sendMQTTmessage(String topic, String message) {
  if(!client.connected()) {
    reconnectMQTT();
  }
  client.publish(topic.c_str(), message.c_str());
}

//should look at varying the +-0.25 to to optimize time on/off
void checkHeating() {
  //should be a max temperature set and check that before keeping pins turned on
  if (overrideIO == true) {
    return;
  }
//  Serial.print("In checkHeating current is: " + String(currentTemp) + " set is: " + String(setTemp));
  if (currentTemp < setTemp-1.00) {
    digitalWrite(led, HIGH); //Turn on LED
    digitalWrite(ssr, HIGH);//turn on ssr
    heating = true;
    
  }
  else if (currentTemp > setTemp+1.00) {
    digitalWrite(led, LOW); //turn off LED
    digitalWrite(ssr, LOW); //turn off ssr
    heating=false;
  }
//  else {
//    client.publish("therm/main", "Temp is currently within +-0.5C of setTemp");
//  }
}


void setup() {
  Serial.begin(115200);
  Serial.println("Booting");

  //disable WiFi until we need it
  WiFi.mode(WIFI_OFF);
  WiFi.forceSleepBegin();
  delay(1);

  //Try to read WiFi settings from RTC mem
  rtcValid = false;
  if (ESP.rtcUserMemoryRead(0,(uint32_t*)&rtcData, sizeof(rtcData))) {
    // Calculate the CRC of what we just read from RTC memory, but skip the first 4 bytes as that's the checksum itself.
    uint32_t crc = calculateCRC32(((uint8_t*)&rtcData) + 4, sizeof(rtcData) - 4);
    if (crc == rtcData.crc32) {
      rtcValid = true;
    }
  }

  //setup pins
  pinMode(led, OUTPUT);
  pinMode(ssr, OUTPUT);
  pinMode(tempIn, INPUT);
  delay(10);
  digitalWrite(led, LOW); //turn off LED
  digitalWrite(ssr, LOW);

  //Battery info
  batt = ESP.getVcc()/1023.0F;
  Serial.print("Battery Voltage: ");
  Serial.println(batt);

  //Read Temperature
  measureTemp();

  //WiFi Time
  connectWiFi();

  //set up for MQTT broker
  client.setServer(mqttServer, mqttPort);
  client.setCallback(callback);
  
}

void loop() {
  //checkHeating(); //check to see if we should be heating
  //Should I check if WiFi disconnects?
  if(!client.connected()) {
//    Serial.println("Inside loop reconnectMQTT()");
    reconnectMQTT();
  }
  
  for(int i=0; i<10; i++) {
    client.loop(); //ensure we have sent/received all messages
    delay(100);
  }
  
  checkHeating(); //if we dont need to heat should shut off wifi and only check every DEEPSLEEPTIME interval
  measureTemp();
  sendDataRecord();

  if(!heating && !overrideIO) {
    sendMQTTmessage("therm/main", "Entering a deep sleep");
    Serial.print("Entering a deep sleep");
    client.disconnect();
    WiFi.disconnect(true);
    delay(1);
    ESP.deepSleep(SLEEPTIME, WAKE_RF_DISABLED);    
//    ESP.deepSleep(SLEEPTIME);    
  }
  delay(5000);
  
}










void printTemp() {
  Serial.print("The current room temperature is: ");
  Serial.print(currentTemp);
  Serial.println(" degress C");
  Serial.print("The current set temperature is: ");
  Serial.print(setTemp);
  Serial.println(" degress C");
  //print to MQTT
  
  //String toSend = "The current temperature is: " + String(aveTemp) + " degrees C.";
  String toSend = String(currentTemp);
  const char* toSendChar = toSend.c_str();
  client.publish("therm/CURRENTTEMP", toSendChar);
}




  
