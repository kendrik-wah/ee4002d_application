//Client-side Javascript code for handling heatmap
$(document).ready(function(){

    //connect to the socket server.
    var socket = io.connect('http://' + document.domain + ':' + location.port);
    
    function send_tareCalCommand(cmd) {
    	try {
	    socket.emit('tarecal', cmd);
	    return true;
    	}
    	catch(err) {
    	    console.log(err);
    	    return False;
    	}
    };
    
    document.getElementById('tare').onclick = function() {
//      alert("button tare was clicked");
    	send_tareCalCommand(1);
    }
    document.getElementById('cal').onclick = function() {
    	send_tareCalCommand(2);
//	alert("button calibrate was clicked");
    }
});
