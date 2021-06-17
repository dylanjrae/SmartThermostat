(function() {
    "use strict";

    var basePath = "http://10.0.0.69/smartTherm"; //For production deployment
    // var basePath = ""; //for testing environment


    function getCurrentStatus () {
        $.ajax({
            url: basePath + '/api/currentStatus',
            type: "GET",
            dataType: 'json',
            success: function(result){
                $("#setTemp").text(result.setTemp);
                $("#upstairsTemp").text(result.upstairsTemp);
                $("#downstairsTemp").text(result.downstairsTemp);
                $("#furnaceStatus").text(result.furnaceStatus);
                $("#time").text(result.time);
                $("#date").text(result.date);
            },
            error: function(error){
                console.log('Error ${error}')
            }
        })
    }
    
    
    getCurrentStatus();
    setInterval(getCurrentStatus, 10000);
})()