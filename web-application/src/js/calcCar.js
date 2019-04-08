var calculateCar = async function(){
    var type;
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
    console.log(type);
    let response = await fetch("/getCars/" + type, {
        credentials: 'same-origin'
    });
    let cars = await response.json();

    var innerHTML = `<p>${cars[0].name}</p>`
    $("#car").append(innerHTML)
}