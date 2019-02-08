var getData = async function() {
    /*let response = await fetch("obd/data.json");
    let allData = await response.json();*/
    let response = await fetch("/getOBD");
    let allData = await response.json();
    //console.log("Test: " + allData)
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
    var tmp = allData[0].TIME;
    var startTime = parseInt(tmp.slice(11, 13))*60*60+parseInt(tmp.slice(14, 16))*60+parseFloat(tmp.slice(17));
    var index = 0;
    for ( var i=0; i < allData.length; ++i ) 
    {
        tmp = allData[i].TIME;
        var res = parseInt(tmp.slice(11, 13))*60*60+parseInt(tmp.slice(14, 16))*60+parseFloat(tmp.slice(17));
        //data[0][i] = (Math.floor(res/3600)).toString()+":"+(Math.floor((res/60)%60)).toString()+":"+(Math.floor(res%60)).toString()+"."+((res%1).toString()).slice(2,5);
        if(i > 0 && (res - startTime) < data[0][i-1]) {
            index = i-1;
            break;
        }
        data[0][i] = res - startTime;
        data[1][i] = allData[i].SPEED;
    }

    var speedTrace = {
        type: "scatter",
        mode: "lines",
        name: 'AAPL Low',
        x: data[0],
        y: data[1],
        line: {color: '#7F7F7F'}
    }
      
    var data = [speedTrace];
          
    var layout = {
        title: 'Data', 
    };
    config = {
        'modeBarButtonsToRemove': ['sendDataToCloud', 'hoverClosestCartesian', 'toggleSpikelines', 'resetScale2d', 'hoverCompareCartesian'],
        'displayModeBar': true,
        'displaylogo': false,
        'responsive': true
    }
    Plotly.newPlot('myDiv', data, layout, config);
}
  
getData();