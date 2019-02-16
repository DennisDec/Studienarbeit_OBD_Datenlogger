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
        $("#allTrips").append("<label class='btn btn-secondary active'><input type='checkbox' class='filename' filename='" + file.filename + "' checked autocomplete='off'>" + file.filename + "</label>")
    });
    printMarkers(fn, nof)
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