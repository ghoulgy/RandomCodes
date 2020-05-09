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
      for(var i=0; i < 256; i++) {
        console.log(JSON.stringify(this.toByteArray(r)));  
      }
      console.log(this.toByteArray(r)['message']['payload']);

      return buffer;  
    }
});
