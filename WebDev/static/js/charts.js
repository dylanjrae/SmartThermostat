

//define options for each chart
//get chart elements for each chart
// apply chart specific formatting to each chart
//create data templates without actual data for each chart
//function to generate chart which calls ajax and updates when complete

$(document).ready(function() {

    //config options for gradient chart with purple
    gradientChartOptionsConfigurationWithTooltipPurple = {
        maintainAspectRatio: false,
        legend: {
          display: false
        },
        tooltips: {
          backgroundColor: '#f5f5f5',
          titleFontColor: '#333',
          bodyFontColor: '#666',
          bodySpacing: 4,
          xPadding: 12,
          mode: "nearest",
          intersect: 0,
          position: "nearest",
          callbacks: {
            label: function(tooltipItem, data) {
              var label = data.datasets[tooltipItem.datasetIndex].label || '';
  
              if (label) {
                  label += ': ';
              }
              label += Math.round(tooltipItem.yLabel * 10) / 10 + String.fromCharCode(176) + 'C';
              return label;
            },
          }
        },
        responsive: true,
        scales: {
          yAxes: [{
            barPercentage: 1.6,
            gridLines: {
              drawBorder: false,
              color: 'rgba(29,140,248,0.0)',
              zeroLineColor: "transparent",
            },
            ticks: {
              suggestedMin: 22,
              suggestedMax: 28,
              padding: 20,
              fontColor: "#9a9a9a"
            }
          }],
  
          xAxes: [{
            barPercentage: 1.6,
            gridLines: {
              drawBorder: false,
              color: 'rgba(225,78,202,0.1)',
              zeroLineColor: "transparent",
            },
            ticks: {
              padding: 20,
              fontColor: "#9a9a9a"
            }
          }]
        }
      };

    //config options for bar chart
    gradientBarChartConfiguration = {
        maintainAspectRatio: false,
        legend: {
          display: false
        },
  
        tooltips: {
          backgroundColor: '#f5f5f5',
          titleFontColor: '#333',
          bodyFontColor: '#666',
          bodySpacing: 4,
          xPadding: 12,
          mode: "nearest",
          intersect: 0,
          position: "nearest"
        },
        responsive: true,
        scales: {
          yAxes: [{
  
            gridLines: {
              drawBorder: false,
              color: 'rgba(29,140,248,0.1)',
              zeroLineColor: "transparent",
            },
            ticks: {
              suggestedMin: 60,
              suggestedMax: 120,
              padding: 20,
              fontColor: "#9e9e9e"
            }
          }],
  
          xAxes: [{
  
            gridLines: {
              drawBorder: false,
              color: 'rgba(29,140,248,0.1)',
              zeroLineColor: "transparent",
            },
            ticks: {
              padding: 20,
              fontColor: "#9e9e9e"
            }
          }]
        }
      };

    //Selecting html elements for the charts
    var ctxTwelveHour = document.getElementById("chartLinePurple").getContext("2d");
    var ctxHistoricalChart = document.getElementById("chartBig1").getContext('2d');
    // var ctxBarChart = document.getElementById("CountryChart").getContext("2d");

    //applying gradients to the chart elements
    var gradientStroke = ctxTwelveHour.createLinearGradient(0, 230, 0, 50);
    gradientStroke.addColorStop(1, 'rgba(72,72,176,0.2)');
    gradientStroke.addColorStop(0.2, 'rgba(72,72,176,0.0)');
    gradientStroke.addColorStop(0, 'rgba(119,52,169,0)'); //purple colors

    gradientStroke = ctxHistoricalChart.createLinearGradient(0, 230, 0, 50);
    gradientStroke.addColorStop(1, 'rgba(72,72,176,0.2)');
    gradientStroke.addColorStop(0.2, 'rgba(72,72,176,0.0)');
    gradientStroke.addColorStop(0, 'rgba(119,52,169,0)'); //purple colors

    // gradientStroke = ctxBarChart.createLinearGradient(0, 230, 0, 50);
    // gradientStroke.addColorStop(1, 'rgba(29,140,248,0.2)');
    // gradientStroke.addColorStop(0.4, 'rgba(29,140,248,0.0)');
    // gradientStroke.addColorStop(0, 'rgba(29,140,248,0)'); //blue colors

    var dataTwelveHour = {
      labels: ['-12hr', '-10hr', '-8hr', '-6hr', '-4hr', '-2hr'],
      datasets: [{
        label: "Average temp.",
        fill: true,
        backgroundColor: gradientStroke,
        borderColor: '#d048b6',
        borderWidth: 2,
        borderDash: [],
        borderDashOffset: 0.0,
        pointBackgroundColor: '#d048b6',
        pointBorderColor: 'rgba(255,255,255,0)',
        pointHoverBackgroundColor: '#d048b6',
        pointBorderWidth: 20,
        pointHoverRadius: 4,
        pointHoverBorderWidth: 15,
        pointRadius: 4,
        data: [24, 25, 26, 25, 24, 23],
      }]
    };

    var dataHistorical = {
      labels: ['-24hr', '-22hr', '-20hr', '-18hr', '-16hr', '-14hr', '-12hr', '-10hr', '-8hr', '-6hr', '-4hr', '-2hr'],
      datasets: [{
          label: "Average temp.",
          fill: true,
          backgroundColor: gradientStroke,
          borderColor: '#d346b1',
          borderWidth: 2,
          borderDash: [],
          borderDashOffset: 0.0,
          pointBackgroundColor: '#d346b1',
          pointBorderColor: 'rgba(255,255,255,0)',
          pointHoverBackgroundColor: '#d346b1',
          pointBorderWidth: 20,
          pointHoverRadius: 4,
          pointHoverBorderWidth: 15,
          pointRadius: 4,
          data: [22, 23, 24, 25, 24, 23, 22, 23, 24, 25, 24, 23],
      }]
    };

    var dataBarChart = {
      labels: ['USA', 'GER', 'AUS', 'UK', 'RO', 'BR'],
      datasets: [{
        label: "Countries",
        fill: true,
        backgroundColor: gradientStroke,
        hoverBackgroundColor: gradientStroke,
        borderColor: '#1f8ef1',
        borderWidth: 2,
        borderDash: [],
        borderDashOffset: 0.0,
        data: [53, 20, 10, 80, 100, 45],
      }]
    };


    function prepareTwelveHourChart(ctx, settings) {
      //request for data
      //on success call function that actually creates chart
      var endDateTime = dayjs();
      var startDateTime = endDateTime.subtract(12, 'hour');

      endDateTime = endDateTime.format('YYYY-MM-DD HH:mm:ss');
      startDateTime = startDateTime.format('YYYY-MM-DD HH:mm:ss');
      
      $.ajax({
        url: '/api/historicalTemp?startDateTime='+ startDateTime + '&endDateTime=' + endDateTime + '&intervals=' + 6,
        type: "GET",
        dataType: 'json',
        success: function(result) {
          //prepare and extract data from JSON
          temps = [];
          counts = [];
          for (const key in result) {
            temps.push(result[key][0]);
            counts.push(result[key][1]);

            // console.log(`${key} : ${result[key][0]}`);
          }
          // console.log(temps);
          // console.log(counts);

          //assign new data to chart settings
          settings.data.datasets[0].data = temps;
          //create chart
          var chart = new Chart(ctx, settings);
          return chart;
        },
        error: function(xhr, status, error) {
          //If error log message and use default data
          var err = eval("(" + xhr.responseText + ")");
          console.log(err);
          console.log("Some data may be missing for 12 hour, using default data.");
          var chart = new Chart(ctx, settings);
          return chart;
        }
      })
    }

    function prepareDayWeekMonthChart(ctx, settings) {
      //request for data
      //on success call function that actually creates chart
      
      var tempsDay = [];
      var countsDay = [];
      var dayLabels = ['-24hr', '-22hr', '-20hr', '-18hr', '-16hr', '-14hr', '-12hr', '-10hr', '-8hr', '-6hr', '-4hr', '-2hr'];
      var tempsWeek = [];
      var countsWeek = [];
      var weekLabels = ['-7d', '-6d', '-5d', '-4d', '-3d', '-2d', '-1d'];
      var tempsMonth = [];
      var countsMonth = [];
      var monthLabels = ['-30', '-29', '-28', '-27', '-26', '-25', '-24', '-23', '-22', '-21', '-20', '-19', '-18', '-17', '-16', '-15', '-14', '-13', '-12', '-11', '-10', '-9', '-8', '-7', '-6', '-5', '-4', '-3', '-2', '-1'];
      var endDateTime = dayjs();
      var startDateTime = endDateTime.subtract(24, 'hour');

      endDateTime = endDateTime.format('YYYY-MM-DD HH:mm:ss');
      startDateTime = startDateTime.format('YYYY-MM-DD HH:mm:ss'); 

      $.ajax({
        url: '/api/historicalTemp?startDateTime='+ startDateTime + '&endDateTime=' + endDateTime + '&intervals=' + 12,
        type: "GET",
        dataType: 'json',
        success: function(result) {
          //prepare and extract data from JSON
          for (const key in result) {
            tempsDay.push(result[key][0]);
            countsDay.push(result[key][1]);
            // console.log(`${key} : ${result[key][0]}`);
          }
          //assign new data to chart settings
          settings.data.datasets[0].data = tempsDay;
        },
        error: function(xhr, status, error) {
          //If error log message and use default data
          var err = eval("(" + xhr.responseText + ")");
          console.log(err);
          console.log("Some data may be missing for 24 hour, using default data.");
          tempsDay = [22, 23, 24, 25, 24, 23, 22, 23, 24, 25, 24, 23];
        },
        complete: function() {
          //create chart
          var chart = new Chart(ctx, settings);
          //get day params for week ajax
          endDateTime = dayjs();
          startDateTime = endDateTime.subtract(1, 'week');
          endDateTime = endDateTime.format('YYYY-MM-DD HH:mm:ss');
          startDateTime = startDateTime.format('YYYY-MM-DD HH:mm:ss'); 
          $.ajax({
            url: '/api/historicalTemp?startDateTime='+ startDateTime + '&endDateTime=' + endDateTime + '&intervals=' + 7,
            type: "GET",
            dataType: "json",
            success: function(result) {
              //prepare and extract data from JSON
              for (const key in result) {
                tempsWeek.push(result[key][0]);
                countsWeek.push(result[key][1]);
                // console.log(`${key} : ${result[key][0]}`);
              }
            },
            error: function(xhr, status, error) {
              //If error log message and use default data
              var err = eval("(" + xhr.responseText + ")");
              console.log(err);
              console.log("Some data may be missing for 1 week, using default data.");
              tempsWeek = [22, 24, 22, 26, 27, 23, 24];
            },
            complete: function() {
              endDateTime = dayjs();
              startDateTime = endDateTime.subtract(1, 'month');
              endDateTime = endDateTime.format('YYYY-MM-DD HH:mm:ss');
              startDateTime = startDateTime.format('YYYY-MM-DD HH:mm:ss'); 
              $.ajax({
                url: '/api/historicalTemp?startDateTime='+ startDateTime + '&endDateTime=' + endDateTime + '&intervals=' + 30,
                type: "GET",
                dataType: "json",
                success: function(result) {
                  //prepare and extract data from JSON
                  for (const key in result) {
                    tempsMonth.push(result[key][0]);
                    countsMonth.push(result[key][1]);
                    // console.log(`${key} : ${result[key][0]}`);
                  }
                },
                error: function(xhr, status, error) {
                  //If error log message and use default data
                  var err = eval("(" + xhr.responseText + ")");
                  console.log(xhr.responseText);
                  console.log("Some data may be missing for 1 month, using default data.");
                  tempsMonth = [22, 23, 24, 25, 24, 23, 22, 23, 24, 25, 24, 23, 24, 25, 24, 23, 22, 23, 24, 25, 24, 23, 24, 25, 24, 23, 22, 23, 24, 25, 24, 23];
                }
              })
            }
          })

          $("#0").click(function() {
            var data = chart.config.data;
            data.datasets[0].data = tempsDay;
            data.labels = dayLabels;
            chart.update();
          });

          $("#1").click(function() {
            var data = chart.config.data;
            data.datasets[0].data = tempsWeek;
            data.labels = weekLabels;
            chart.update();
          });

          $("#2").click(function() {
            var data = chart.config.data;
            data.datasets[0].data = tempsMonth;
            data.labels = monthLabels;
            chart.update();
          });
        }
      })
    }

    // function updateDayChart(chart) {
    //     //request for data
    //     //on success call function that actually creates chart
    //     var endDateTime = dayjs();
    //     var startDateTime = endDateTime.subtract(24, 'hour');
  
    //     endDateTime = endDateTime.format('YYYY-MM-DD HH:mm:ss');
    //     startDateTime = startDateTime.format('YYYY-MM-DD HH:mm:ss');
  
    //     $.ajax({
    //       url: '/api/historicalTemp?startDateTime='+ startDateTime + '&endDateTime=' + endDateTime + '&intervals=' + 12,
    //       type: "GET",
    //       dataType: 'json',
    //       success: function(result) {
    //         //prepare and extract data from JSON
    //         temps = [];
    //         counts = [];
    //         for (const key in result) {
    //           temps.push(result[key][0]);
    //           counts.push(result[key][1]);
  
    //           // console.log(`${key} : ${result[key][0]}`);
    //         }
    //         // console.log(temps);
    //         // console.log(counts);
  
    //         //assign new data to chart settings
    //         console.log(chart);
    //         chart.datasets[0].data = temps;
    //         chart.settings.data.labels = ['-24hr', '-22hr', '-20hr', '-18hr', '-16hr', '-14hr', '-12hr', '-10hr', '-8hr', '-6hr', '-4hr', '-2hr'];
    //         chart.update();
    //       },
    //       error: function(xhr, status, error) {
    //         //If error log message and use default data
    //         var err = eval("(" + xhr.responseText + ")");
    //         console.log(err);
    //         console.log("Some data may be missing for 24 hour chart, using default data.");
    //         console.log(chart);

    //         chart.datasets[0].data = [22, 23, 24, 25, 24, 23, 22, 23, 24, 25, 24, 23];
    //         chart.settings.data.labels = ['-24hr', '-22hr', '-20hr', '-18hr', '-16hr', '-14hr', '-12hr', '-10hr', '-8hr', '-6hr', '-4hr', '-2hr'];
    //         chart.update();
    //       }
    //     })
    //   }

    
    var twelveHourChart = prepareTwelveHourChart(ctxTwelveHour, {
                            type: 'line',
                            data: dataTwelveHour,
                            options: gradientChartOptionsConfigurationWithTooltipPurple
                          });

    var dayWeekMonthChart = prepareDayWeekMonthChart(ctxHistoricalChart, {
                              type: 'line',
                              data: dataHistorical,
                              options: gradientChartOptionsConfigurationWithTooltipPurple
                            });


    // generateSetTempHistoryChart();
});