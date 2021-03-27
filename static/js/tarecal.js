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
    	    return false;
    	}
    };
    
    function send_recordCommand() {
    	try {
	    socket.emit('record');
	    return true;
    	}
    	catch(err) {
    	    console.log(err);
    	    return false;
    	}
    };
    
    document.getElementById('tare').onclick = function() {
    	send_tareCalCommand(1);
    }
    document.getElementById('cal').onclick = function() {
    	send_tareCalCommand(2);
    }
    document.getElementById('store').onclick = function() {
        send_recordCommand();
    }
    
    socket.on('midtarecal', function() {
    	var updateList = Array.from(document.getElementById('updates').children);
    	var updateList = updateList.map(function(element) {return element.outerHTML});
    	
    	updateList.reverse();
    	updateList.push('<div class="notification-div" id="notification-div"><div class="notification-text-div"><h3 class="notification-header" id="notification-header">I\'m sorry, but hang on...</h3><p class="notification" id="notification">Floormat is still taring</p></div></div>');
    	updateList.reverse();
    
        if (updateList.length >= 10) {
            updateList = updateList.slice(0, updateList.length-1);
        }
        
        var newList = "";
        for (var i = 0; i < updateList.length; i++) {
            newList = newList + updateList[i];
        }
        
        document.getElementById('updates').innerHTML = newList;
    })
});	
