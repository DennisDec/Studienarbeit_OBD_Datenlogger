var now = Date.now();

$('[data-toggle="datepicker"]').datepicker({
  filter: function(date, view) {
    /*console.log(date)
    console.log(date.getMonth())
    console.log(date.getDay())
    console.log(date.getDate())
    if (date.getDay() === 0 && view === 'day') {
      return false; // Disable all Sundays, but still leave months/years, whose first day is a Sunday, enabled.
    }*/
    return true;
  }
});
/*
$('[data-toggle="datepicker"]').datepicker({
  filter: function(date, view) {
    var vin = document.getElementById('VIN').value;
    vin = (vin === "") ? "none" : vin; 
    console.log(vin)

    fetch("/getDatesOfTrips/" + vin, {
      credentials: 'same-origin'
    }).then(function(response) {
      let promise = response.json()
      promise.then(function(dates) {
        var dd = date.getDate();
        var mm = date.getMonth()+1; //January is 0!
        var yyyy = date.getFullYear();
        if(dd<10) {
            dd = '0'+dd
        }
        if(mm<10) {
            mm = '0'+mm
        }
        datePicker = mm + '-' + dd + '-' + yyyy;
        console.log(datePicker)
        for(var i = 0; i < dates.length; i++) {
          console.log(datePicker === dates[i].date)
          if (datePicker === dates[i].date && view === 'day') {
            return true; 
          } else {
            console.log("test")
            return false;
          }
        }
        if(view === 'day') {
          console.log("test")
          return false;
        }
      })
    })
  }
});*/