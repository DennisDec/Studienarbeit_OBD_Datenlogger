var getData = async function(filename, name) {
    // sends a request with credentials included
    let response = await fetch("/getOBD/" + filename, {
        credentials: 'same-origin'
    });
    let allData = await response.json();

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

    // Sources: https://plot.ly/javascript/configuration-options
    //          https://community.plot.ly/t/remove-options-from-the-hover-toolbar/130/11 
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