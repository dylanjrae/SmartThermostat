#include <PubSubClient.h>
#include <ESP8266WiFi.h>
#include <WiFiClient.h>
#include <ArduinoOTA.h>
#include <WiFiUdp.h>
#include <NTPClient.h>


#include <ESP8266mDNS.h>
#include <ESP8266WebServer.h>

#ifndef STASSID
#define STASSID "NUTHOUSE_2.4"
#define STAPSK  "pmwpmwpmw"
#define MQTTHOST "10.0.0.69"
#define MQTTPORT 1883
#endif

void ICACHE_RAM_ATTR pulseDetect();

void handleRoot();
void handleNotFound();
void handleSetTemp();
ESP8266WebServer server(80);

const char* ssid = STASSID;
const char* password = STAPSK;

const char* mqttServer = MQTTHOST;
const int mqttPort = MQTTPORT;
const char* mqttUser = NULL;
const char* mqttPassword = NULL;
const char* willTopic = "therm/STATUS";
const int willQoS = 0;
boolean willRetain = true;
const char* willMessage = "F";

const int led = D2;
const int ssr = D6;
const int tempIn = D5;
boolean overrideIO = false;
boolean heating = false;

int hour;


float setTemp = 24;
float currentTemp=0;

volatile unsigned int pulseCount = 0;

const long utcOffsetInSeconds = -25200;

WiFiUDP ntpUDP;
NTPClient timeClient(ntpUDP, "north-america.pool.ntp.org", utcOffsetInSeconds);

WiFiClient espClient;
PubSubClient client(espClient);


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
      setNewTemp(message.toFloat());
    }
    
  Serial.println();
}

void connectWifi() {
    WiFi.begin(ssid, password);
    Serial.print("Connecting to WiFi Network: ");
    Serial.print(ssid);
    Serial.println(" ...");

    int i = 0;
    while (WiFi.status() != WL_CONNECTED) {
      delay(1000);
      Serial.print(++i); Serial.print(' ');
      //light blinks every other second when connecting then goes hard on after connecting
      if (i % 2 == 1) {
        digitalWrite(led, HIGH);
      }
      else {
        digitalWrite(led, LOW);
      }
    }
    digitalWrite(led, LOW);
      
    Serial.println("\n");
    Serial.print("Connection established in "); Serial.print(i); Serial.println(" seconds!");
    Serial.print("IP address: ");
    Serial.println(WiFi.localIP());
  }

void connectMQTT() {
  //set up and connect to mqtt broker
  client.setServer(mqttServer, mqttPort);
  client.setCallback(callback);

  while (!client.connected()) {
    Serial.println("Attempting to connect to MQTT broker...");
    if (client.connect("ESP8266Client", mqttUser, mqttPassword, willTopic, willQoS, willRetain, willMessage)) {
      Serial.println("Connected to mqtt broker!");
    }
    else {
      Serial.print("mqtt broker connection failed with state: ");
      Serial.println(client.state());
      delay(2000);
    }
    //while trying to connec tto mqtt do the following tasks
      recordTemp();
      checkTemp();
      ArduinoOTA.handle();
  }

  client.publish("therm/main", "Welcome, the ESP8266 board is here.");
  client.publish("therm/STATUS", "TRUE", true);
  client.subscribe("therm/TEMPSET");
  client.subscribe("therm/OVERRIDE");
}

void startWebServer() {
  if (MDNS.begin("thermostat")) {              // Start the mDNS responder for esp8266.local
      Serial.println("mDNS responder started");
    } else {
      Serial.println("Error setting up MDNS responder!");
    }
  
    server.on("/", HTTP_GET, handleRoot);        // Call the 'handleRoot' function when a client requests URI "/"
    server.on("/SetTemp", HTTP_POST, handleSetTemp); // Call the 'handleLogin' function when a POST request is made to URI "/login"
    server.onNotFound(handleNotFound);           // When a client requests an unknown URI (i.e. something other than "/"), call function "handleNotFound"
  
    server.begin();                            // Actually start the server
    Serial.println("HTTP server started");
}

void handleRoot() {
  server.send(200, "text/html", "<form action=\"/SetTemp\" method=\"POST\"><p>Welcome to the <b>NutHouse</b> Thermostat :)</p><img src=\"https://canadiantire.scene7.com/is/image/CanadianTire/1753194_1?defaultImage=image_na_EN&imageSet=CanadianTire/1753194_1?defaultImage=image_na_EN&id=-lir53&fmt=jpg&fit=constrain,1&wid=339&hei=200\" alt=\"NUTTT\"><p>The current room temperature is: <b>" + String(currentTemp) + "</b> degrees C</p><p>The current set temperature is: <b>" + String(setTemp) + "</b> degrees C</p> <p>Furnace on? (it's a boolean): " + String(heating) + "</p><input type=\"text\" name=\"setTemp\" placeholder=\"Enter new set temp\"></br></br><input type=\"submit\" value=\"Set Now!\"></form>");
}

void handleNotFound(){
  server.send(404, "text/plain", "404: Not found"); // Send HTTP status 404 (Not Found) when there's no handler for the URI in the request
}

void handleSetTemp() {                         // If a POST request is made to URI /login
  if( ! server.hasArg("setTemp") || server.arg("setTemp") == NULL) { // If the POST request doesn't have username and password data
    server.send(400, "text/plain", "400: Invalid Request");         // The request is invalid, so send HTTP status 400
    return;
  }
  if(server.arg("setTemp").toFloat() < 25.0 && server.arg("setTemp").toFloat() > 15.0) { // If temperature is in range
    setNewTemp(server.arg("setTemp").toFloat());
    server.send(200, "text/html", "<h2>The temperature was successfuly set to " + server.arg("setTemp") + " degrees C!</h2><p>And remember...<b>PMW</b> always</p>");
  } 
  else {                                                               // temp out of range
    server.send(401, "text/plain", "401: Unauthorized/Error");
  }
}

float getTemp() {//when called adds the reading to the array, once at the end it rewrites from the start
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
  if (pulseCount == 0)
    return 1000;//FAIL - never got a pulse

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
    return 1000;//FAIL
  }

  detachInterrupt(digitalPinToInterrupt(tempIn));//done with the interrupt
  float temperatureC = 256.000 * pulseCount / 4096.000 - 50;//conversion
  //see 7.3.2 Output Transfer Function in Datasheet

  return temperatureC;//throw the temp back
}

void ICACHE_RAM_ATTR pulseDetect() { //Pulse counter interrupt function
  pulseCount++;
}

void updateTime() {
  hour = timeClient.getHours();
}

void checkSchedule() {
  //plus 1 for daylight savings time
  if (hour +1 == 22) { 
    setNewTemp(17.0);
  }
  else if (hour+1 == 5) {
    setNewTemp(25);
  }
  else {
    return;
  }
}

void recordTemp() {
  currentTemp = getTemp();
}

void setNewTemp(float newTemp) {
  setTemp = newTemp;
  Serial.print("The new set temp is: ");
  Serial.println(String(setTemp));

  String toSend = "The new temperature has been set to: " + String(setTemp) + " degrees C.";
  const char* toSendChar = toSend.c_str();
  client.publish("therm/main", toSendChar);
}


//when called prints the average of the last x readings
void printTemp() {
  Serial.print("The current room temperature is: ");
  Serial.print(currentTemp);
  Serial.println(" degress C");
  Serial.print("The current set temperature is: ");
  Serial.print(setTemp);
  Serial.println(" degress C");
  //print to MQTT
  
  //String toSend = "The current temperature is: " + String(currentTemp) + " degrees C.";
  String toSend = String(currentTemp);
  const char* toSendChar = toSend.c_str();
  client.publish("therm/CURRENTTEMP", toSendChar);
}

//should look at varying the +-0.25 to to optimize time on/off
void checkTemp() {
  //should be a max temperature set and check that before keeping pins turned on
  if (overrideIO == true) {
    return;
  }
  
  if (currentTemp < setTemp-1.00) {
    //digitalWrite(led, HIGH); //Turn on LED
    digitalWrite(ssr, HIGH);//turn on ssr
    heating = true;
  }
  else if (currentTemp > setTemp+1.00) {
    //digitalWrite(led, LOW); //turn off LED
    digitalWrite(ssr, LOW); //turn off ssr
    heating=false;
  }
//  else {
//    client.publish("therm/main", "Temp is currently within +-0.5C of setTemp");
//  }
}


void setup() {
  //setup pins
  pinMode(led, OUTPUT);
  pinMode(ssr, OUTPUT);
  digitalWrite(led, LOW); //turn off LED
  digitalWrite(ssr, LOW);

  //connect to wifi
  Serial.begin(115200);
  Serial.println("Booting");
  
  connectWifi();
  connectMQTT();
  startWebServer();
  timeClient.begin();

  ArduinoOTA.onStart([]() {
    String type;
    if (ArduinoOTA.getCommand() == U_FLASH) {
      type = "sketch";
    } else { // U_FS
      type = "filesystem";
    }

    // NOTE: if updating FS this would be the place to unmount FS using FS.end()
    Serial.println("Start updating " + type);
  });
    
  ArduinoOTA.onEnd([]() {
    Serial.println("\nEnd");
  });
  
  ArduinoOTA.onProgress([](unsigned int progress, unsigned int total) {
    Serial.printf("Progress: %u%%\r", (progress / (total / 100)));
  });
  
  ArduinoOTA.onError([](ota_error_t error) {
    Serial.printf("Error[%u]: ", error);
    if (error == OTA_AUTH_ERROR) {
      Serial.println("Auth Failed");
    } else if (error == OTA_BEGIN_ERROR) {
      Serial.println("Begin Failed");
    } else if (error == OTA_CONNECT_ERROR) {
      Serial.println("Connect Failed");
    } else if (error == OTA_RECEIVE_ERROR) {
      Serial.println("Receive Failed");
    } else if (error == OTA_END_ERROR) {
      Serial.println("End Failed");
    }
  });
  ArduinoOTA.begin();
  recordTemp();
}
  

void loop() {
  ArduinoOTA.handle();
  timeClient.update();
  server.handleClient();

  if(WiFi.status() == WL_CONNECTION_LOST) {
    Serial.println("WiFi connection lost! Reconnecting...");
    connectWifi();
    recordTemp();
    checkTemp();
  }
  if(WiFi.status() == WL_DISCONNECTED) {
    Serial.println("WiFi disconnected! Reconnecting...");
    connectWifi();
    recordTemp();
    checkTemp();
  }
  if(!client.connected()){
    connectMQTT();
    recordTemp();
    checkTemp();
    ArduinoOTA.handle();
  }
  client.loop();

  //if currently heating stay in same loop
  //if not heating go into deep sleep

  //record temp measures temp and updates new ave
  updateTime();
  recordTemp();
  checkTemp();
  printTemp();
  checkSchedule();
//  String toSend = "The current hour is: " + String(hour);
//  const char* toSendChar = toSend.c_str();
//  client.publish("therm/main", toSendChar);

  //could write temp schedukle into flash so it is still there when it boots up after deep sleep
  //Serial.println("The current hour is: " + String(hour));
  Serial.println("before therm/FURNACE, and heating is:" + String(heating));
  if(heating) {
    client.publish("therm/FURNACE", "1");
    Serial.println("Insisde if therm/FURNACE, and heating is:" + String(heating));
  }
  else {
    client.publish("therm/FURNACE", "0");
    Serial.println("Inside else therm/FURNACE, and heating is:" + String(heating));
  }

  //should make a message board everyone can post to

//could also implement deep sleep by checking the temp a set numbers of times then sleeping

//DEEP SLEEP MODE HERE
//   if(!heating && !overrideIO) {
//should also make sure not having a ota (MQTT message to say OTA incoming, dont go to sleep
//    client.publish("therm/main", "Entering a deep sleep");
//    Serial.print("Entering a deep sleep");
//    delay(1000);
//    ESP.deepSleep(20e6);
//    delay(10);
//            
//  }
  delay(5000);
}
