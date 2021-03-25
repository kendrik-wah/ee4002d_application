//Client-side Javascript code for handling heatmap
$(document).ready(function(){

    //connect to the socket server.
    var socket = io.connect('http://' + document.domain + ':' + location.port);

    socket.on('reinitialized', function(msg) {
       document.getElementById('init-datetime').innerHTML = msg.datetime;
    });

    //receive details from server
    socket.on('newheatmap', function(msg) {

        var cell = "";
        for (var i = 0; i < msg.rows; i++) {
            for (var j = 0; j < msg.cols; j++) {
                cell = cell + '<div class=\'tile\' style=\"background-color: ' + msg.heatmap[i][j] + '; width: 80px; height: 80px;\";></div>';
            };
        };

        document.getElementById('tile-grid').innerHTML = cell;
        
        var updateList = Array.from(document.getElementById('updates').children);
        var updateList = updateList.map(function(element) {return element.outerHTML});
        
        updateList.reverse();
        
        if (msg.datetime == undefined) {
            updateList.push('<div class="notification-div" id="notification-div"><div class="notification-text-div"><h3 class="notification-header" id="notification-header">Heatmap initialized</h3><p class="notification" id="notification">Awaiting connection to prototype floormat.</p></div></div>');
        }
        
        else if (msg.completeTared == false && msg.isTared == true) {
            updateList.push('<div class="notification-div" id="notification-div"><div class="notification-text-div"><h3 class="notification-header" id="notification-header">Heatmap is taring</h3><p class="notification" id="notification">Map updated at: ' + msg.datetime + '.</p></div></div>');
        }
        else if (msg.completeTared == true && msg.isTared == true) {
	    updateList.push('<div class="notification-div" id="notification-div"><div class="notification-text-div"><h3 class="notification-header" id="notification-header">Heatmap tared</h3><p class="notification" id="notification">Last tared at: ' + msg.datetime + '.</p></div></div>');
        }
        else {
            updateList.push('<div class="notification-div" id="notification-div"><div class="notification-text-div"><h3 class="notification-header" id="notification-header">Heatmap updated</h3><p class="notification" id="notification">Last updated at: ' + msg.datetime + '.</p></div></div>');
        }
        
        
        updateList.reverse();
    
        if (updateList.length >= 10) {
            updateList = updateList.slice(0, updateList.length-1);
        }
        
        var trollList = updateList.map(function(element) {return element});
        
        var newList = "";
        for (var i = 0; i < updateList.length; i++) {
            newList = newList + updateList[i];
        }
        
        document.getElementById('updates').innerHTML = newList;
    });
    
    socket.on('record-notify', function(msg) {
        
        var updateList = Array.from(document.getElementById('updates').children);
        var updateList = updateList.map(function(element) {return element.outerHTML});
    	updateList.reverse();
    	
    	if (msg.flag == true) {
    	    updateList.push('<div class="notification-div" id="notification-div"><div class="notification-text-div"><h3 class="notification-header" id="notification-header">Data saving started</h3><p class="notification" id="notification">' + "Recording started at: " + msg.datetime + '</p></div></div>');
    	}
    	else {
    	    updateList.push('<div class="notification-div" id="notification-div"><div class="notification-text-div"><h3 class="notification-header" id="notification-header">Data saving stopped</h3><p class="notification" id="notification">' + "Recording stopped at: " + msg.datetime + '</p></div></div>');
    	}

    	updateList.reverse();
    
        if (updateList.length >= 10) {
            updateList = updateList.slice(0, updateList.length-1);
        }
        
        var newList = "";
        for (var i = 0; i < updateList.length; i++) {
            newList = newList + updateList[i];
        }
        
        document.getElementById('updates').innerHTML = newList;
    });
});


