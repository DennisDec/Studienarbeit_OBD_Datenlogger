var os = require( 'os' );
var interfaces = os.networkInterfaces();

function getIP() {
    /*var addresses = [];
    var add = null;
    for (var k in interfaces) {
        for (var k2 in interfaces[k]) {
            var address = interfaces[k][k2];
            if (address.family === 'IPv4' && !address.internal) {
                addresses.push(address.address);
                if (address.address.slice(0, 3) === '192') {
                    add = address.address
                }
            }
        }
    }
    console.log(add);
    return add;*/
    console.log("Local IP:" + require('my-local-ip')())
    return require('my-local-ip')();
}

module.exports = getIP;