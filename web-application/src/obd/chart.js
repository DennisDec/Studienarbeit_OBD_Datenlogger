var getData = async function() {
    let response = await fetch("obd/data.json");
    let allData = await response.json();
    
    var time = [];
    var speed = [];/*
    var rpm = [];
    var engine_load = [];
    var maf = [];
    var temperature = [];
    var pedal = [];
    var afr = [];
    var fuel_level = [];*/
    var data = [time, speed/*, rpm, engine_load, maf, temperature, pedal, afr, fuel_level*/];
    var tmp = allData[0].time;
    var startTime = parseInt(tmp.slice(11, 13))*60*60+parseInt(tmp.slice(14, 16))*60+parseFloat(tmp.slice(17));
    var index = 0;
    for ( var i=0; i < allData.length; ++i ) 
    {
        tmp = allData[i].time;
        var res = parseInt(tmp.slice(11, 13))*60*60+parseInt(tmp.slice(14, 16))*60+parseFloat(tmp.slice(17));
        //data[0][i] = (Math.floor(res/3600)).toString()+":"+(Math.floor((res/60)%60)).toString()+":"+(Math.floor(res%60)).toString()+"."+((res%1).toString()).slice(2,5);
        if(i > 0 && (res - startTime) < data[0][i-1]) {
            index = i-1;
            break;
        }
        data[0][i] = res - startTime;
        data[1][i] = allData[i].speed;
    }
    var ctx = document.getElementById("myChart");
    var myChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data[0],
            datasets: [{
                data: data[1],
                lineTension: 0,
                backgroundColor: 'transparent',
                borderColor: '#007bff',
                borderWidth: 2,
                pointBackgroundColor: '#007bff',
                pointRadius: 0
            }]
        },
        options: {
            scales: {
                yAxes: [{
                    ticks: {
                        beginAtZero: false
                    }
                }]
            },
            legend: {
                display: false,
            }
        }
    });
}

getData();