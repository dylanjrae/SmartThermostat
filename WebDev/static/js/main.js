$(document).ready(function() {
    $().ready(function() {
        "use strict";
        
// *********UPDATING DATA METRICS*******************
        // var basePath = "http://10.0.0.69/smartTherm"; //For production deployment DEBUG=False, Testing = True
        // var basePath = "http://70.72.206.93/"; 
        var basePath = "http://smarttherm.dylanrae.ca"; 
        // var basePath = ""; //for testing environment
        var request

        var knob = pureknob.createKnob(130,130);

        // Set properties.
        knob.setProperty('angleStart', -0.75 * Math.PI);
        knob.setProperty('angleEnd', 0.75 * Math.PI);
        knob.setProperty('colorFG', '#4081DF');
        knob.setProperty('readonly', true);
        knob.setProperty('trackWidth', 0.4);
        knob.setProperty('valMin', 14);
        knob.setProperty('valMax', 25);

        // Set initial value.
        knob.setValue(20);

        // Create element node.
        const node = knob.node();

        // Add it to the DOM.
        const elem = document.getElementById('knob');
        elem.appendChild(node);

        function getCurrentStatus () {
            $.ajax({
                url: basePath + '/api/currentStatus',
                type: "GET",
                dataType: 'json',
                success: function(result){
                    $("#setTemp").text(result.setTemp);
                    knob.setValue(result.setTemp);
                    $("#upstairsTemp").text(result.upstairsTemp);
                    $("#downstairsTemp").text(result.downstairsTemp);
                    $(".furnace-status-result").text(result.furnaceStatus);
                    $("#time").text(result.time);
                    $("#date").text(result.date);
                    // print(result.furnaceStatus.toString());
                    if (result.furnaceStatus.toString() == "ON") {
                        console.log("here");
                        if ($(".furnace-status-icon").length != 0) {
                            $(".furnace-status-icon").attr('data', "ON");
                        }
                    }
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
                $("#setTempResult").text("Success! Allow up to 1min for the change to be seen system wide.")
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
    });
});