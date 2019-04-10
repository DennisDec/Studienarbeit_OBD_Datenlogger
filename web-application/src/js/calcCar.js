var averageTripLength = 0;
var numberOfTrips = 0;
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
    var deltaToAverage = averageTripLength;
    for(let i = 0; i < cars.length; i++) {
        range[i] = (cars[i].capacity / (cars[i].consumption * energyConsumptionFactor)) * 100;
        if(((range[i] - averageTripLength) < deltaToAverage) && (range[i] > averageTripLength)) {
            deltaToAverage = range[i] - averageTripLength;
            bestCar = i;
        }
        console.log("Range: " + range[i])
    }

    var innerHTML = `<p>${cars[bestCar].name}</p>`
    $("#car").append(innerHTML)
}