var map = L.map( 'map', {
    center: [20.0, 5.0],
    minZoom: 2,
    zoom: 2
});

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

var printMarkers = async function() {
    let response = await fetch("maps/markers.json");
    let markers = await response.json();
    markers = await removeNull(markers);
    console.log("Markeranzahl: " + markers.length)
    for ( var i=0; i < markers.length; ++i ) 
    {
        L.marker( [markers[i].lat, markers[i].lng] )
            .bindPopup( '<p>' + markers[i].route_name + '</p>' )
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
}

var removeNull = function(markers) {
    let markerList = new Array();
    for ( var i=0; i < markers.length; ++i ) 
    {
        console.log((i+1) + ". marker: " + markers[i].lng + ", " + markers[i].lat);
        if(markers[i].lng === null || markers[i].lat === null) {
            continue;
        }
        markerList.push({ 
            "lat": markers[i].lat,
            "lng": markers[i].lng
        });
    }
    return markerList;
}

printMarkers();