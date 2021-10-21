// $(document).ready(function() {
function mainFunc(isLoggedIn) {
    // $().ready(function() {
        "use strict";
        
        // *********UPDATING DATA METRICS*******************
        // var basePath = "http://10.0.0.69/smartTherm"; //For production deployment DEBUG=False, Testing = True
        // var basePath = "http://70.72.206.93/"; 
        // var basePath = "http://smarttherm.dylanrae.ca"; 
        var basePath = ""; //for testing environment
        // var basePath = window.location.hostname
        var request

        var knob = pureknob.createKnob(130,130);

        // Set properties.
        knob.setProperty('angleStart', -0.75 * Math.PI);
        knob.setProperty('angleEnd', 0.75 * Math.PI);
        knob.setProperty('colorFG', '#ba54f5');
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
                        if ($(".blob").length != 0) {
                            $(".blob").attr('data', "ON");
                        }
                    }
                },
                error: function(error){
                    console.log('Error ${error}')
                }
            })
        }

        function getSetTempHistory() {
            var endDateTime = dayjs();
            //24 hours for now but change to 1 week after testing
            var startDateTime = endDateTime.subtract(1, 'week');

            endDateTime = endDateTime.format('YYYY-MM-DD HH:mm:ss');
            startDateTime = startDateTime.format('YYYY-MM-DD HH:mm:ss'); 
            var setTempRecords = [];
            $.ajax({
                url: basePath + '/api/historicalSetTemp?startDateTime=' + startDateTime + '&endDateTime=' + endDateTime,
                type: "GET",
                dataType: 'json',
                success: function(result) {
                    for (const key in result) {
                        setTempRecords.push(result[key])
                      }
                    //   console.log(setTempRecords);
                    //   console.log(setTempRecords[1][3])
                    var trHTML = '';
                    $.each(setTempRecords, function(i, o) {
                        trHTML += '<tr><td>' + setTempRecords[i][0] +
                                  '</td><td>' + setTempRecords[i][1] +
                                  '</td><td>' + setTempRecords[i][2] +
                                  '</td><td class="alignRight">' + setTempRecords[i][3] + "\xB0C" +
                                  '</td></tr>';
                        // console.log(setTempRecords[i]);
                    });
                    $('#setTempTable').append(trHTML);

                },
                error: function(xhr, status, error) {
                    var err = eval("(" + xhr.responseText + ")");
                    console.log(err);
                }
            })
        }
        getSetTempHistory();

        if(isLoggedIn) {
            
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
        }
    
        else {
            $("#setTempForm").submit(function(event) {
                event.preventDefault();
                "use strict";
                window.$("#ovrly").fadeIn();
                window.$("#login").show();
                window.$("#login").animate({top: "250"});
            })
        }
        
        
        getCurrentStatus();
        setInterval(getCurrentStatus, 10000);
    // });

    
}
    
// });