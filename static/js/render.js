//Client-side Javascript code for handling heatmap
$(document).ready(function(){
    //connect to the socket server.
    var socket = io.connect('http://' + document.domain + ':' + location.port + '/test');
    console.log(document.domain, location.port);

    //receive details from server
    socket.on('newheatmap', function(msg) {
//        console.log(msg.heatmap, msg.cols, msg.rows);

        var cell = "";
        for (var i = 0; i < msg.cols; i++) {
            for (var j = 0; j < msg.rows; j++) {
                cell = cell + '<div class=\'heatmap\' style=\"background-color: ' + msg.heatmap[i][j] + "\";></div>";
                console.log(cell);
            };
        };

        document.getElementById('tile').innerHTML = cell;
//        $("#tile").html(cell);

//        // maintain a list of ten numbers
//        if (numbers_received.length >= 10){
//            numbers_received.shift()
//        }
//        numbers_received.push(msg.number);
//        numbers_string = '';
//        for (var i = 0; i < numbers_received.length; i++){
//            numbers_string = numbers_string + '<p>' + numbers_received[i].toString() + '</p>';
//        }
//        $('#heatmap').html(numbers_string);
    });
});