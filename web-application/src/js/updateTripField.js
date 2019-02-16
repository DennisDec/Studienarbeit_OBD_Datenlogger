var update = async function() {
    var date = (document.getElementById('datepicker').value).replace(/\//g,  '-')
    if(document.getElementById('datepicker').value === "") {
        var today = new Date();
        var dd = today.getDate();
        var mm = today.getMonth()+1; //January is 0!
        var yyyy = today.getFullYear();
        if(dd<10) {
            dd = '0'+dd
        }
        if(mm<10) {
            mm = '0'+mm
        }
        date = mm + '-' + dd + '-' + yyyy;
    }
    console.log(date);
    let response = await fetch("/getTrips/" + date, {
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
        $("#allTrips").append("<label class='btn btn-secondary active'><input type='checkbox' class='filename' filename='" + file.filename + "' checked autocomplete='off'>Fahrt " + nof + "</label>")
    });
    printMarkers(fn, nof);
    $("#charts").empty()
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
                //console.log($(this).prop('checked'));
                //console.log($(".test").length);
                for(var g = 0; g < $(".filename").length; g++) {
                    //console.log($(".test:eq(" + g + ")").prop('checked'));
                    if($(".filename:eq(" + g + ")").prop('checked')) {
                        //console.log($(".test:eq(" + g + ")").attr('test'));
                        filenames.push($(".filename:eq(" + g + ")").attr('filename'));
                        nof++;
                    }
                }
                console.log(filenames);
                printMarkers(filenames, nof);
                $("#charts").empty()
                for(var h = 1; h <= nof; h++) {
                    $("#charts").append("<div id='Fahrt " + h + "'></div>")
                    getData(filenames[h-1], "Fahrt " + h);
                }
            });
        }
    });
}

update()

/*
function post(path, params, method) {
    method = method || "post";
 
    const form = document.createElement("form");
    form.setAttribute("method", method);
    form.setAttribute("action", path);
 
 
    for (const key in params) {
        if (params.hasOwnProperty(key)) {
            const hiddenField = document.createElement("input");
            hiddenField.setAttribute("type", "hidden");
            hiddenField.setAttribute("name", key);
            hiddenField.setAttribute("value", params[key]);
 
            form.appendChild(hiddenField);
        }
    }
 
    document.body.appendChild(form);
    form.submit();
}*/
/*let response = await fetch("/dashboard", {
        method: "POST",
        credentials: 'same-origin',
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(data)
    });*/
    //post("/dashboard", {"date": document.getElementById('datepicker').value})