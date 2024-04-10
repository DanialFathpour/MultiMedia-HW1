// Defines the websocket and the gateway for it
var gateway = `ws://${window.location.hostname}/ws`;
var websocket;
// Inits web socket when the page loads
window.addEventListener('load', onload);
function initWebSocket() {
    console.log('Trying to open a WebSocket connection…');
    websocket = new WebSocket(gateway);
    websocket.onopen = onOpen;
    websocket.onclose = onClose;
    websocket.onmessage = onMessage;
}

//Inits stuff
function onload(event) {
    initWebSocket();
	initButton();
}

//Gets sensor readings
function getReadings(){
    websocket.send("getReadings");
}

// When websocket is established, call the getReadings() function
function onOpen(event) {
    console.log('Connection opened');
    getReadings();
}

//Closes the sebsocket connection
function onClose(event) {
    console.log('Connection closed');
    setTimeout(initWebSocket, 2000);
}

// Function that receives the message from the ESP32 with the readings
function onMessage(event) {
    console.log(event.data);
    var myObj = JSON.parse(event.data);
    var keys = Object.keys(myObj);

    for (var i = 0; i < keys.length; i++){
        var key = keys[i];
        document.getElementById(key).innerHTML = myObj[key];
    }
	
	var state;
    if (event.data == "1"){
      state = "ON";
    }
    else{
      state = "OFF";
    }
    document.getElementById('state').innerHTML = state;
}

// Inits the button
  function initButton() {
    document.getElementById('button').addEventListener('click', toggle);
  }

// Sends the 'toggle' request to change the LED state
  function toggle(){
    websocket.send('toggle');
  }
 
// Defines the chart  
  var chartT = new Highcharts.Chart({
  chart:{ renderTo : 'chart-light' },
  title: { text: 'Light' },
  series: [{
    showInLegend: false,
    data: []
  }],
  plotOptions: {
    line: { animation: false,
      dataLabels: { enabled: true }
    },
    series: { color: '#059e8a' }
  },
  xAxis: { type: 'datetime',
    dateTimeLabelFormats: { second: '%H:%M:%S' }
  },
  yAxis: {
    title: { text: 'Light' }
  },
  credits: { enabled: false }
});

// Sets a time interval (here is 2s) between 2 request for updating the chart
setInterval(function ( ) {
  var xhttp = new XMLHttpRequest();
  xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
      var x = (new Date()).getTime(),
          y = parseFloat(this.responseText);
      //console.log(this.responseText);
      if(chartT.series[0].data.length > 40) {
        chartT.series[0].addPoint([x, y], true, true, true);
      } else {
        chartT.series[0].addPoint([x, y], true, false, true);
      }
    }
  };
  xhttp.open("GET", "/light", true);
  xhttp.send();
}, 2000 ) ;