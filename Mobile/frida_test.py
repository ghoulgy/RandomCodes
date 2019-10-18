import frida
import sys
import json


def on_message(message, data):
    if message['type'] == 'send':
        print("[*] {0}".format(message['payload']))
    else:
        print(message)


jscode = """
Java.perform(function () {
    // Function to hook is defined here
    var MainActivity = Java.use("<Your Activity>");

    // Check input String
    const StringBuilder = Java.use('java.lang.StringBuilder');

    var strings = StringBuilder.toString.implementation = function () {
            var result = this.toString();
            return result;
    };

    var string_class = Java.use("java.lang.String");

    MainActivity.<Your Function>.implementation = function(s) {
      var buffer = Java.array('byte', [ 145, 209, 170, 8, 204, 61 ]);
      return Java.array('byte', [ 145, 209, 170, 8, 204, 61 ]);
    }
});
"""
process = frida.get_usb_device().attach('<Your Process To be Attached>')
script = process.create_script(jscode)
script.on('message', on_message)
print('[*] Running Frida')
script.load()
sys.stdin.read()