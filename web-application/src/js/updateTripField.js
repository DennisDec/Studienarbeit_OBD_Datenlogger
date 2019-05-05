var displayData = function() {
    $("#headerVinEingabe").css("display", "")
    $("#sidebar").css("display", "")
    $("#firstPart").css("display", "")
    $("#secondPart").css("display", "")
    $("#dataPart").css("display", "")
    $("#VinEingabe").css("display", "none")
    var vin = document.getElementById('firstVin').value;  
    $("#VIN").val(vin);
    document.getElementById('VINButton').click()
}

var update = async function() {
    var vin = document.getElementById('VIN').value;
    console.log(vin)
    vin = (vin === "") ? "none" : vin; 
    var dateArray = (document.getElementById('datepicker').value).split(".")
    var date = (dateArray[1] + '-' + dateArray[0]+ '-' + dateArray[2])
    if(document.getElementById('datepicker').value === "") {
        var today = new Date();
        var dd = today.getDate();
        var mm = today.getMonth() + 1; //January is 0!
        var yyyy = today.getFullYear();
        if(dd < 10) {
            dd = '0' + dd
        }
        if(mm < 10) {
            mm = '0' + mm
        }
        date = mm + '-' + dd + '-' + yyyy;
    }
    console.log(date);
    let response = await fetch("/getTrips/" + date + "/" + vin, {
        credentials: 'same-origin'
    });
    let filenames = await response.json();
    console.log(filenames)
    var nof = 0;
    var fn = [];
    $("#allTrips").empty()
    filenames.forEach(file => {
        console.log(file.filename)
        fn.push(file.filename)
        nof++;
        var innerHTML = `<label class='tripButton btn btn-secondary active'>
                            <input type='checkbox' class='filename' filename='${file.filename}' checked autocomplete='off'>
                                Fahrt ${nof}<br>
                                <div class='buttonText'>
                                    Startzeit: ${file.starttime} Uhr<br>
                                    gef. KM: ${file.totalKM} km<br>
                                </div>
                        </label>`
        $("#allTrips").append(innerHTML)
    });
    printMarkers(fn, nof);
    $("#charts").empty()
    if(nof === 0) {
        $("#dataPart").css("display", "none")
    } else {
        $("#dataPart").css("display", "")
    }
    for(var h = 1; h <= nof; h++) {
        console.log("Filename: " + fn[h-1])
        $("#charts").append("<div id='Fahrt " + h + "'></div>")
        getData(fn[h-1], "Fahrt " + h);
    }
    $(function() {
        console.log($(".filename").length);
        //console.log($(".test:eq(0)").attr('test'));
        for(var i = 0; i < $(".filename").length; i++) {
            $(".filename:eq(" + i + ")").change(function(){
                var filenames = [];
                var nof = 0;
                $("#charts").empty()
                //console.log($(this).prop('checked'));
                //console.log($(".test").length);
                for(var g = 0; g < $(".filename").length; g++) {
                    //console.log($(".test:eq(" + g + ")").prop('checked'));
                    if($(".filename:eq(" + g + ")").prop('checked')) {
                        //console.log($(".test:eq(" + g + ")").attr('test'));
                        filenames.push($(".filename:eq(" + g + ")").attr('filename'));
                        nof++;
                        $("#charts").append("<div id='Fahrt " + (g + 1) + "'></div>")
                        getData($(".filename:eq(" + g + ")").attr('filename'), "Fahrt " + (g + 1));
                    }
                }
                console.log(filenames);
                printMarkers(filenames, nof);
            });
        }
    });
}

update()