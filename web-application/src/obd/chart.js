var getData = async function(filename, name) {
    /*let response = await fetch("obd/data.json");
    let allData = await response.json();*/
    // sends a request with credentials included
    let response = await fetch("/getOBD/" + filename, {
        credentials: 'same-origin'
    });
    let allData = await response.json();
    //console.log(response)
    //console.log("Test: " + allData.SPEED)
    var time = allData.TIME;
    var speed = allData.SPEED;
    var rpm = allData.RPM;/*
    var engine_load = [];
    var maf = [];
    var temperature = [];
    var pedal = [];
    var afr = [];
    var fuel_level = [];*/
    var data = [time, speed, rpm/*, engine_load, maf, temperature, pedal, afr, fuel_level*/];
    /*var tmp = allData.TIME[0];
    console.log(tmp)
    var startTime = parseInt(tmp.slice(11, 13))*60*60+parseInt(tmp.slice(14, 16))*60+parseFloat(tmp.slice(17));
    var index = 0;
    for ( var i=0; i < allData.TIME.length; ++i ) 
    {
        tmp = allData.TIME[i];
        //console.log(tmp)
        var res = parseInt(tmp.slice(11, 13))*60*60+parseInt(tmp.slice(14, 16))*60+parseFloat(tmp.slice(17));
        //data[0][i] = (Math.floor(res/3600)).toString()+":"+(Math.floor((res/60)%60)).toString()+":"+(Math.floor(res%60)).toString()+"."+((res%1).toString()).slice(2,5);
        if(i > 0 && (res - startTime) < data[0][i-1]) {
            index = i-1;
            break;
        }
        data[0][i] = res - startTime;
    }*/

    var speedTrace = {
        type: "scatter",
        mode: "lines",
        name: 'Speed',
        x: data[0],
        y: data[1],
        yaxis: 'y2',
        line: {color: '#7F7F7F'}
    }

    var rpmTrace = {
        type: "scatter",
        mode: "lines",
        name: 'RPM',
        x: data[0],
        y: data[2],
        line: {color: '#1f77b4'}
    }
    
    var data = [speedTrace, rpmTrace];
        
    var layout = {
        title: name,
        width: 800,
        xaxis: 
        {
            domain: [0.25, 1],
            showgrid: false
        },
        yaxis: 
        {
            title: 'RPM',
            titlefont: {color: '#1f77b4'},
            tickfont: {color: '#1f77b4'},
            showgrid: false
        },
        yaxis2: 
        {
            title: 'Speed',
            titlefont: {color: '#7F7F7F'},
            tickfont: {color: '#7F7F7F'},
            anchor: 'free',
            overlaying: 'y',
            side: 'left',
            position: 0.15,
            showgrid: false
        }
    };
    config = {
        'modeBarButtonsToRemove': ['sendDataToCloud', 'hoverClosestCartesian', 'toggleSpikelines', 'resetScale2d', 'hoverCompareCartesian'],
        'displayModeBar': true,
        'displaylogo': false,
        'responsive': true
    }
    Plotly.newPlot(name, data, layout, config);
}

//getData("undefined");