(function() {
    "use strict";

    var basePath = "http://10.0.0.69/smartTherm"; //For production deployment
    // var basePath = ""; //for testing environment
    var request

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

    $("#setTempForm").submit(function(event) {
        event.preventDefault();

        if (request) {
            request.abort();
        }

        var $form = $(this);
        var $inputs = $form.find("input, select, buttom, textarea");

        var serializedData = $form.serialize();

        $inputs.prop("disabled", true);

        request = $.ajax({
            url: basePath + "/api/setTemp",
            type: "POST",
            data: serializedData
        });

        // Callback handler that will be called on success
        request.done(function (response, textStatus, jqXHR){
            // Log a message to the console
            console.log("Hooray, it worked!");
            $("#setTempResult").text("Success!")
        });

        // Callback handler that will be called on failure
        request.fail(function (jqXHR, textStatus, errorThrown){
            // Log the error to the console
            console.error(
                "The following error occurred: "+
                textStatus, errorThrown
            );
            $("#setTempResult").text("There was an error sending the new temperature.")
        });

        // Callback handler that will be called regardless
        // if the request failed or succeeded
        request.always(function () {
            // Reenable the inputs
            $inputs.prop("disabled", false);
        });
    })
    
    
    getCurrentStatus();
    setInterval(getCurrentStatus, 10000);
})()