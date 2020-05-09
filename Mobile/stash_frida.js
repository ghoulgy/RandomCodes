// Byte to String
function byteToString(arr) { 
  if(typeof arr === 'string') { 
    return arr; 
  } 
  var str = '', 
  _arr = arr; 
  for(var i = 0; i < _arr.length; i++) { 
    var one = _arr[i].toString(2), 
        v = one.match(/^1+?(?=0)/); 
    if(v && one.length == 8) { 
      var bytesLength = v[0].length; 
      var store = _arr[i].toString(2).slice(7 - bytesLength); 
      for(var st = 1; st < bytesLength; st++) { 
          store += _arr[st + i].toString(2).slice(2); 
      } 
      str += String.fromCharCode(parseInt(store, 2)); 
      i += bytesLength - 1; 
    } else { 
      str += String.fromCharCode(_arr[i]); 
    } 
  } 
  return str; 
}

Java.perform(function () {
    // Function to hook is defined here
    
    var MainActivity = Java.use("<Activity>");
    // Check input String
    const StringBuilder = Java.use('java.lang.StringBuilder');

    var strings = StringBuilder.toString.implementation = function () {
            var result = this.toString();
            return result;
    };

    MainActivity.<Activity>.implementation = function(s) {
      var buffer = Java.array('byte', [ 228, 99, 161, 233 ,249, 51 ]);
      /* String to Byte
      var ch, st, re = [];
      for (var i = 0; i < s.length; i++) {
        ch = s.charCodeAt(i);
        st = [];
        st.push(ch & 0xFF);
        re = re.concat(st.reverse());
      }
      var buffer = Java.array('byte', re);
      console.log(buffer[0]);
      */
      return buffer;
    }
});
  
Java.perform(function () {
    // Function to hook is defined here
    var MainActivity = Java.use("<Activity>");
    var byt = Java.use("android.content.Intent");
    var IO = Java.use("org.apache.commons.io.IOUtils");

    MainActivity.onCreate.implementation = function(v) {
      this.onCreate(v);  
    }

    // byt.getByteArrayExtra.implementation = function(s) {
    //   console.log(this.getByteArrayExtra(s)[0] & 0xff );
    //   var buffer = Java.array('byte', [ 13, 37, 42 ]);
    //   return buffer;  
    // }


    IO.toByteArray.overload('java.io.InputStream').implementation = function(r) {
      var st = [];
      for(var i=0; i < 256; i++) {
        st.push(i);
      }
      var buffer = Java.array('byte', st);
      // console.log(r);
      // if(r == "android.content.res.AssetManager$AssetInputStream@8b99f4a") {
      // for(var i=0; i < 256; i++) {
      //   console.log(JSON.stringify(this.toByteArray(r)));
      // }
      send(this.toByteArray(r));

      return buffer;  
    }

    // Modify return value
    var string_class = Java.use("java.lang.String");
    MainActivity.<Activity>.implementation = function(s) {
      // var buffer = Java.array('byte', [0]);
      var new_string = string_class.$new("");
      var buffer = this.transform(new_string);
      send(buffer);
      return buffer;
    }

    MainActivity.<Activity>.implementation = function(s) {
      var buffer = Java.array('byte', [ 145, 209, 170, 8, 204, 61 ]);
      return Java.array('byte', [ 145, 209, 170, 8, 204, 61 ]);
    }
});
