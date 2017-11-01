// This application uses express as its web server
// for more info, see: http://expressjs.com
var express = require('express');

// create a new express server
var app = express();

// serve the files out of ./public as our main files
app.use(express.static(__dirname + '/app'));

// Start the server
const PORT = process.env.PORT || 9102;
app.listen(PORT, () => {
  console.log(`App listening on port ${PORT}`);
  console.log('Press Ctrl+C to quit.');
});
// [END app]

app.get('/env', function (apprequest, appresponse){
  env = { APIENDPOINTURL: process.env.APIENDPOINTURL || 'http://localhost:9101' };
  /*env = { APIENDPOINTURL: process.env.APIENDPOINTURL || 'http://192.168.99.100:31101' };*/
  appresponse.json(env);
});

app.get('*', function (apprequest, appresponse){
  appresponse.sendFile(__dirname + '/app/index.html');
});