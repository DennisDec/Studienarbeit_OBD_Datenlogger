var map = L.map( 'map', {
    center: [20.0, 5.0],
    minZoom: 2,
    zoom: 2
});

var printMarkers = function(filename, nof) {
    map.remove();
    
    map = L.map( 'map', {
        center: [20.0, 5.0],
        minZoom: 2,
        zoom: 2
    });

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    console.log(nof)

    for(var g = 0; g < nof; g++) {
        fetch("/getGPS/" + filename[g], {
            credentials: 'same-origin'
        }).then(function(response) {
            let promise = response.json()
            promise.then(function(markers) {

                removeNull(markers, function(markers){

                    for ( var i=0; i < markers.length; ++i ) 
                    {
                        var tmp = 0;
                        if(i === 0 || i === (markers.length - 1)) {
                            tmp = 1;
                        }
                        L.marker( [markers[i].lat, markers[i].lng], {opacity: tmp})
                            //TODO: show start and stop time
                            .bindPopup( '<p>Start-Time' + markers[i].route_name + '</p>' )
                            .addTo( map );

                        if ((i + 1)  < markers.length) {
                            var latlngs = Array();
                            latlngs.push({ 
                                "lat": markers[i].lat,
                                "lng": markers[i].lng
                            });
                            latlngs.push({ 
                                "lat": markers[i+1].lat,
                                "lng": markers[i+1].lng
                            });
                            var polyline = L.polyline(latlngs, {color: 'blue'}).addTo(map);
                        }
                    }
                    var bounds = L.latLngBounds(markers);
                    map.fitBounds(bounds);
            
                })
        
            })
        })
    }
}

var removeNull = function(markers, callback) {
    let markerList = new Array();
    for ( var i=0; i < markers.GPS_Lat.length; ++i ) 
    {
        //console.log((i+1) + ". marker: " + markers.GPS_Long[i] + ", " + markers.GPS_Lat[i]);
        if(markers.GPS_Long[i] === null || markers.GPS_Lat[i] === null) {
            console.log("Test")
            continue;
        }
        markerList.push({ 
            "lat": markers.GPS_Lat[i],
            "lng": markers.GPS_Long[i]
        });
    }
    //return markerList;
    callback(markerList)
}

printMarkers(["undefined"], 1);