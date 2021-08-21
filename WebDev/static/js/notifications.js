$(document).ready(function() {
        "use strict";
        function getSetTempHistory() {
            var endDateTime = dayjs();
            //24 hours for now but change to 1 week after testing
            var startDateTime = endDateTime.subtract(1, 'week');

            endDateTime = endDateTime.format('YYYY-MM-DD HH:mm:ss');
            startDateTime = startDateTime.format('YYYY-MM-DD HH:mm:ss'); 
            var setTempRecords = [];
            $.ajax({
                url: '/api/historicalSetTemp?startDateTime=' + startDateTime + '&endDateTime=' + endDateTime,
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
            });
        }
        getSetTempHistory();
});