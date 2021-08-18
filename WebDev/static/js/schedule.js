function mainFunc(isLoggedIn) {
    "use strict";

    function getCurrentSchedule() {
        var scheduleRecords = [];
        $.ajax ({
            url: '/api/viewSchedule',
            type: "GET",
            dataType: 'json',
            success: function(result){
                for (const key in result) {
                    scheduleRecords.push(result[key])
                  }
                //   console.log(setTempRecords);
                //   console.log(setTempRecords[1][3])
                var trHTML = '';
                $.each(scheduleRecords, function(i, o) {
                    var preHeat;
                    if(scheduleRecords[i][3] == 'on') {
                        preHeat = 'Yes'
                    }
                    else {
                        preHeat = 'No';
                    }

                    trHTML += '<tr><td>' + scheduleRecords[i][0] +
                              '</td><td>' + scheduleRecords[i][2] +
                              '</td><td>' + preHeat +
                              '</td><td class="alignRight">' + scheduleRecords[i][1] +
                              '</td></tr>';
                    // console.log(setTempRecords[i]);
                });
                $('#scheduleTable').append(trHTML);
            },
            error: function(error){
                console.log('Error ${error}')
                $("#scheduleResult").text("There was an error retrieving your schedule :(")
            }
        })
    }
    getCurrentSchedule();

    if(isLoggedIn) {
        //endpoint only accepts POST, default get
        $("#setScheduleForm").attr('method', 'POST');
        $("#deleteScheduleForm").attr('method', 'POST');
    }

    else {
        $("#setScheduleForm").submit(function(event) {
            event.preventDefault();
            "use strict";
            window.$("#ovrly").fadeIn();
            window.$("#login").show();
            window.$("#login").animate({top: "250"});
        })

        $("#deleteScheduleForm").submit(function(event) {
            event.preventDefault();
            "use strict";
            window.$("#ovrly").fadeIn();
            window.$("#login").show();
            window.$("#login").animate({top: "250"});
        })
    }
}