//Client-side Javascript code for handling heatmap
$(document).ready(function(){

    //connect to the socket server.
    var socket = io.connect('http://' + document.domain + ':' + location.port + '/test');

    //receive details from server
    socket.on('newheatmap', function(msg) {

        var cell = "";
        for (var i = 0; i < msg.rows; i++) {
            for (var j = 0; j < msg.cols; j++) {
                cell = cell + '<div class=\'heatmap\' style=\"background-color: ' + msg.heatmap[i][j] + '; width: 100px; height: 100px;\";></div>';
            };
        };

        document.getElementById('tile').innerHTML = cell;
    });
});
