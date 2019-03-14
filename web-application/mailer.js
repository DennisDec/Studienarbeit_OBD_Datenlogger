var nodemailer = require('nodemailer');
var jwt = require('jsonwebtoken');
var getIP = require('./getIP.js');
var fs = require('fs');

function mailer(id, email, mode) {
    jwt.sign(
    {
        user: id,
    },
        process.env.MAIL_SECRET,
    {
        expiresIn: '1d',
    },
    (err, emailToken) => {
        var transporter = nodemailer.createTransport({
            service: 'gmail',
            auth: {
                user: process.env.MAIL_NAME,
                pass: process.env.MAIL_PASSWORD
            }
        });
        var add = getIP();
        if (mode === "confirmation") {
            const url = `http://${add}:3000/confirmation/${emailToken}`;
            var mailOptions = {
                from: process.env.MAIL_NAME,
                to: email,
                subject: 'Confirm your email!',
                html: `Please click this link to confirm your email: <a href="${url}">${url}</a>`
            };
        } else if (mode === "resetpw") {
            const url = `http://${add}:3000/resetpw${emailToken}`;
            var mailOptions = {
                from: process.env.MAIL_NAME,
                to: email,
                subject: 'Reset your password!',
                html: `Please click this link to reset your password: <a href="${url}">${url}</a>`
            };
        } else if (mode === "getIP") {
            const url = `http://${add}:3000`;
            var ip = require("./ip.json");
            console.log("IP-test: "+ ip.ip);
            if (ip.ip != add) {
                fs.writeFileSync("./ip.json", JSON.stringify({"ip": add}));
                mail = email;
            } else {
                mail = none;
            }
            var mailOptions = {
                from: process.env.MAIL_NAME,
                to: mail,
                subject: 'Your Server-Homepage!',
                html: `Please click this link to connect to the Server-Homepage: <a href="${url}">${url}</a>`
            };
        }
        transporter.sendMail(mailOptions, async (error, info) => {
            if (error) {
                console.log(error);
            } else {
                console.log('Email sent: ' + info.response);
            }
        });
    });
}
module.exports = mailer;