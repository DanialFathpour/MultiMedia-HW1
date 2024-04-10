#include <ESP8266WiFi.h>
#include <ESPAsyncTCP.h>
#include <ESPAsyncWebServer.h>
#include "LittleFS.h"



// Should be replaced with your network credentials
const char* ssid = "modem";
const char* password = "123456";




// Defines LED pin and state
bool ledState = 0;
const int ledPin = 2;

// Creates AsyncWebServer object on port 80 mmeans HTTP
AsyncWebServer server(80);

// Creates a WebSocket object
AsyncWebSocket ws("/ws");

// Timer variables
unsigned long lastTime = 0;  
unsigned long timerDelay = 2000; // Means it reads ans sends values every 2s

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

// Texts LED state using the Websocket object 
void notifyClients() {
  ws.textAll(String(ledState));
}

// Handles the incoming websocket message from the client
void handleWebSocketMessage(void *arg, uint8_t *data, size_t len) {
  AwsFrameInfo *info = (AwsFrameInfo*)arg;
  if (info->final && info->index == 0 && info->len == len && info->opcode == WS_TEXT) {
    data[len] = 0;
    if (strcmp((char*)data, "toggle") == 0) {
      ledState = !ledState;
    }
    notifyClients();
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

// Automatically handles requests and checks for filesystems (HTML, CSS, JS)
  server.serveStatic("/", LittleFS, "/");

// Starts server
  server.begin();
}

//-----------------------------------------------------------------------------------------------------------------------------------------
void loop() {
  digitalWrite(ledPin, ledState);

// Manages the clients that are connected the server
  ws.cleanupClients();
}