var averageTripLength = 0;
var numberOfTrips = 0;
var longestTrip = 0;
var vConsumption = 0;

var calculateCar = async function(){
    var type;
    var energyConsumptionFactor;
    var bestCar;
    console.log("averageTripLength: "+ averageTripLength)
    console.log((document.getElementById('input01')).value)
    switch ((document.getElementById('input01')).value) {
        case "1":
            type = "micro"
            break;
        case "2":
            type = "mini"
            break;
        case "3":
            type = "medium"
            break;
        case "4":
            type = "van"
            break;
        case "5":
            type = "luxury"
            break;
        default:
            break;
    }
    switch ((document.getElementById('input02')).value) {
        case "1":
            energyConsumptionFactor = 0.9
            break;
        case "2":
            energyConsumptionFactor = 1.0
            break;
        case "3":
            energyConsumptionFactor = 1.1
            break;
        default:
            break;
    }

    console.log(type);
    let response = await fetch("/getCars/" + type, {
        credentials: 'same-origin'
    });

    let cars = await response.json();
    var range = [];
    var count = 0;
    var deltaToAverage = averageTripLength;
    for(let i = 0; i < cars.length; i++) {
        range[i] = (cars[i].capacity / (cars[i].consumption * energyConsumptionFactor)) * 100;
        if(((range[i] - averageTripLength) < deltaToAverage) && (range[i] > averageTripLength)) {
            deltaToAverage = range[i] - averageTripLength;
            bestCar = i;
        } else {
            count++;
        }
        console.log("Range: " + range[i])
    }
    //falls kein Fahrzeug passt, muss das beste gewählt werden
    if(count == cars.length) {
        bestCar = 0;
        for(let i = 0; i < cars.length; i++) {
            if(range[i] > range[bestCar]) {
                bestCar = i;
            }
        }
    }
    $("#car").empty()
    $("#range").empty()
    $("#eConsumption").empty()
    $("#averageTripLength").empty()
    $("#longestTrip").empty()
    $("#chargeStops").empty()
    $("#vConsumption").empty()
    $("#table").css("display", "")
    if(averageTripLength != 0) {
        var innerHTML = `${cars[bestCar].name}`
        $("#car").append(innerHTML)
        innerHTML = `${Math.round(range[bestCar])}km`
        $("#range").append(innerHTML)
        innerHTML = `${cars[bestCar].consumption.toFixed(2)}kWh/100km`
        $("#eConsumption").append(innerHTML)
        innerHTML = `${Math.round(averageTripLength)}km`
        $("#averageTripLength").append(innerHTML)
        innerHTML = `${Math.round(longestTrip)}km`
        $("#longestTrip").append(innerHTML)
        innerHTML = `${Math.floor(longestTrip / range[bestCar])}`
        $("#chargeStops").append(innerHTML)
        innerHTML = `${vConsumption.toFixed(2)}kWh/100km`
        $("#vConsumption").append(innerHTML)
    } else {
        var innerHTML = `noch keine Fahrt`
        $("#car").append(innerHTML)
        $("#range").append(innerHTML)
        $("#eConsumption").append(innerHTML)
        $("#averageTripLength").append(innerHTML)
        $("#longestTrip").append(innerHTML)
        $("#chargeStops").append(innerHTML)
        $("#vConsumption").append(innerHTML)
    }
    $(function(){
        $('[data-toggle="tooltip"]').tooltip();
    })
}
