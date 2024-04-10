#include <Arduino.h>
#include <ESP8266WiFi.h>
#include <ESPAsyncTCP.h>
#include <ESPAsyncWebServer.h>
#include "LittleFS.h"
#include <Arduino_JSON.h>
#include <Hash.h>


// Should be replaced with your network credentials
const char* ssid = "Daniel_modem";
const char* password = "MAUXX93633";

// Defines LED pin and state
bool ledState = 0;
const int ledPin = 2;

// Creates AsyncWebServer object on port 80 mmeans HTTP
AsyncWebServer server(80);

// Creates a WebSocket object
AsyncWebSocket ws("/ws");

// Json Variable to Hold Sensor Readings
JSONVar readings;

// Timer variables
unsigned long lastTime = 0;  
unsigned long timerDelay = 2000; // Means it reads ans sends values every 2s

// Gets Sensor Readings and return JSON object
String getSensorReadings(){
  readings["light"] = String(analogRead(A0));
  String jsonString = JSON.stringify(readings);
  return jsonString;
}

String readsensor() {
  float t = analogRead(A0);
  return String(t);
}

// Initializes FileSystem uploader
void initFS() {
  if (!LittleFS.begin()) {
    Serial.println("An error has occurred while mounting LittleFS");
  }
  else{
   Serial.println("LittleFS mounted successfully");
  }
}

// Initializes WiFi
void initWiFi() {
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi ..");
  while (WiFi.status() != WL_CONNECTED) {
    Serial.print('.');
    delay(1000);
  }
  Serial.println(WiFi.localIP());
}

// Texts sensor readings and LED state using the Websocket object 
void notifyClients(String sensorReadings) {
  ws.textAll(String(ledState));
  ws.textAll(sensorReadings);
}

// Handles the incoming websocket message from the client
void handleWebSocketMessage(void *arg, uint8_t *data, size_t len) {
  AwsFrameInfo *info = (AwsFrameInfo*)arg;
  if (info->final && info->index == 0 && info->len == len && info->opcode == WS_TEXT) {
    String sensorReadings = getSensorReadings();
    Serial.print(sensorReadings);  
    data[len] = 0;
    if (strcmp((char*)data, "toggle") == 0) {
      ledState = !ledState;
    }
    notifyClients(sensorReadings);
  }
}

// Checks wether any client is connected/disconnected
void onEvent(AsyncWebSocket *server, AsyncWebSocketClient *client, AwsEventType type, void *arg, uint8_t *data, size_t len) {
  switch (type) {
    case WS_EVT_CONNECT:
      Serial.printf("WebSocket client #%u connected from %s\n", client->id(), client->remoteIP().toString().c_str());
      break;
    case WS_EVT_DISCONNECT:
      Serial.printf("WebSocket client #%u disconnected\n", client->id());
      break;
    case WS_EVT_DATA:
      handleWebSocketMessage(arg, data, len);
      break;
    case WS_EVT_PONG:
    case WS_EVT_ERROR:
      break;
  }
}

// Initializes Websocket
void initWebSocket() {
  ws.onEvent(onEvent);
  server.addHandler(&ws);
}


//--------------------------------------------------------------------------------------------------------------------------------------
void setup(){
  Serial.begin(115200);

  pinMode(ledPin, OUTPUT);
  digitalWrite(ledPin, LOW);
  
  initFS();
  initWiFi();
  initWebSocket();

  // Web Server Root URL
  server.on("/", HTTP_GET, [](AsyncWebServerRequest *request) {
    request->send(LittleFS, "/index.html", "text/html");
  });

  // Web Server request for the plot
  server.on("/light", HTTP_GET, [](AsyncWebServerRequest *request){
    request->send_P(200, "text/plain", readsensor().c_str());
  });

//
  server.serveStatic("/", LittleFS, "/");

  // Starts server
  server.begin();
}

//-----------------------------------------------------------------------------------------------------------------------------------------
void loop() {

// Sends the data every 2s
  if ((millis() - lastTime) > timerDelay) {
    String sensorReadings = getSensorReadings();
    Serial.print(sensorReadings);
    notifyClients(sensorReadings);
    lastTime = millis();
  }

  digitalWrite(ledPin, ledState);

// 
  ws.cleanupClients();
}