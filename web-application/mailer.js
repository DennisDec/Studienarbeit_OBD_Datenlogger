var nodemailer = require('nodemailer');
var jwt = require('jsonwebtoken');

function mailer(id, email, mode) {
    if (mode === "confirmation") {
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
            const url = `http://localhost:3000/confirmation/${emailToken}`;
            var mailOptions = {
                from: process.env.MAIL_NAME,
                to: email,
                subject: 'Confirm your email!',
                html: `Please click this link to confirm your email: <a href="${url}">${url}</a>`
            };
            transporter.sendMail(mailOptions, async (error, info) => {
                if (error) {
                    console.log(error);
                } else {
                    console.log('Email sent: ' + info.response);
                }
            });
        });
    } else if (mode === "resetpw") {
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
            const url = `http://localhost:3000/resetpw${emailToken}`;
            var mailOptions = {
                from: process.env.MAIL_NAME,
                to: email,
                subject: 'Confirm your email!',
                html: `Please click this link to confirm your email: <a href="${url}">${url}</a>`
            };
            transporter.sendMail(mailOptions, async (error, info) => {
                if (error) {
                    console.log(error);
                } else {
                    console.log('Email sent: ' + info.response);
                }
            });
        });
    }
}
module.exports = mailer;