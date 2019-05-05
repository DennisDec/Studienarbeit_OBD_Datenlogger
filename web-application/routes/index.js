var express = require('express');
var router = express.Router();
var passport = require('passport');
const bcrypt = require('bcrypt');
var fs = require('fs');
var jwt = require('jsonwebtoken');

var mailer = require('../mailer.js');

const saltRounds = 10;

// GET home page
router.get('/', function(req, res) {
  res.render('home', { title: 'Home', home: true });
});

// Route to confirm the email
router.get('/confirmation/:token', function(req, res) {
  var id = jwt.verify(req.params.token, process.env.MAIL_SECRET);
  console.log("User to be confirmed: " + id);
  var db = require('../db.js');
  db.query('UPDATE users SET confirmed = 1 WHERE id = ?', [id.user], function(err, results, fields) {
    if(err) throw err;
  });
  res.redirect('/login');
});

// GET information about the cars of the given car type
router.get('/getCars/:token', authenticationMiddleware(), function(req, res) {
  var db = require('../db.js');
  console.log("Car type: " + req.params.token)
  db.query('SELECT consumption, capacity, power, name FROM cars WHERE type=?', [req.params.token], function(err, results, fields) {
    if(err) throw err;
    var data = [];
    for(var i = 0; i < results.length; i++) {
      data.push({
        consumption: results[i].consumption,
        capacity: results[i].capacity,
        power: results[i].power,
        name: results[i].name
      })
    }
    res.send(data);
  });
});

// GET the obd data of the given filename
router.get('/getOBD/:token', authenticationMiddleware(), function(req, res) {
  var address = '../../datafiles/' + req.params.token;
  var data = JSON.parse(fs.readFileSync(address, 'utf8'));
  delete data['GPS_Long'];
  delete data['GPS_Lat'];
  delete data['GPS_Alt'];
  res.send(data);
});

// GET the gps data of the given filename
router.get('/getGPS/:token', authenticationMiddleware(), function(req, res) {
  var address = '../../datafiles/' + req.params.token;
  var data = JSON.parse(fs.readFileSync(address, 'utf8'));
  delete data['AMBIANT_AIR_TEMP'];
  delete data['RPM'];
  delete data['RELATIVE_ACCEL_POS'];
  delete data['FUEL_LEVEL'];
  delete data['MAF'];
  delete data['COMMANDED_EQUIV_RATIO'];
  delete data['SPEED'];
  delete data['ENGINE_LOAD'];
  res.send(data);
});

// GET the gps data of the given vin
router.get('/getAllGPS/:vin', authenticationMiddleware(), function(req, res) {
  var vin = req.params.vin;
  var db = require('../db.js');
  db.query('SELECT filename, vin, totalKM, energyConsumption FROM data', function(err, results, fields) {
    if(err) throw err;
    var tmp = [];
    for(var i = 0; i < results.length; i++) {
      // the vin is saved as a hash in the database, so it has to be compared with bcrypt
      if(bcrypt.compareSync(vin, results[i].vin)) {
        tmp.push({
          filename: results[i].filename,
          totalKM: results[i].totalKM,
          energyConsumption: results[i].energyConsumption
        })
      }
    }
    var data = [];
    var averageTripLength = 0;
    var longestTrip = 0;
    var vConsumption = 0;
    for(var i = 0; i < tmp.length; i++) {
      console.log("File: " + tmp[i].filename)
      var address = '../../datafiles/' + tmp[i].filename;
      data[i] = JSON.parse(fs.readFileSync(address));
      delete data[i]['AMBIANT_AIR_TEMP'];
      delete data[i]['RPM'];
      delete data[i]['RELATIVE_ACCEL_POS'];
      delete data[i]['FUEL_LEVEL'];
      delete data[i]['MAF'];
      delete data[i]['COMMANDED_EQUIV_RATIO'];
      delete data[i]['SPEED'];
      delete data[i]['ENGINE_LOAD'];
      // Calculate the average trip length and the total energy consumption
      averageTripLength += tmp[i].totalKM / tmp.length;
      if(longestTrip <= tmp[i].totalKM) {
        longestTrip = tmp[i].totalKM;
      }
      vConsumption += tmp[i].energyConsumption;
    }
    console.log("averageTripLength: " + averageTripLength)
    // Add general information to the end of the data object 
    data.push({
      averageTripLength: averageTripLength,
      longestTrip: longestTrip,
      vConsumption: vConsumption / (tmp.length * averageTripLength) * 100
    })
    res.send(data);
  });
});

// GET the waiting points for the given vin
router.get('/getWaitingTime/:vin', authenticationMiddleware(), function(req, res) {
  var vin = req.params.vin;
  var db = require('../db.js');
  db.query('SELECT date, starttime, endtime, endLat, endLong, endDate, vin FROM data', function(err, results, fields) {
    if(err) throw err;
    var tmp = [];
    for(var i = 0; i < results.length; i++) {
      if(bcrypt.compareSync(vin, results[i].vin)) {
        tmp.push({
          date: results[i].date,
          starttime: results[i].starttime,
          endtime: results[i].endtime,
          endLat: results[i].endLat,
          endLong: results[i].endLong,
          endDate: results[i].endDate
        })
      }
    }
    var data = [];
    // Calculate the waiting time by creating the dates with end and starttime and subtract them 
    for(var i = 0; i < (tmp.length - 1); i++) {
      var tmp1 = (tmp[i].endtime).split(":");
      var date1 = (tmp[i].endDate).split("-");
      var tmp2 = (tmp[i+1].starttime).split(":");
      var date2 = (tmp[i+1].date).split("-");
      time1 = new Date(date1[2], date1[0], date1[1], tmp1[0], tmp1[1], tmp1[2]);
      time2 = new Date(date2[2], date2[0], date2[1], tmp2[0], tmp2[1], tmp2[2]);
      // Subtraction of two dates delivers the difference in seconds
      dateTotal = time2 - time1;
      data.push({
        waitingTime: dateTotal, 
        gpsLat: tmp[i].endLat,
        gpsLong: tmp[i].endLong
      });
    }
    res.send(data);
  });
});

// GET dashboard page; only accessable for authenticated users
router.get('/dashboard', authenticationMiddleware(), function(req, res, next) {
  res.render('dashboard', { title: 'Dashboard', dashboard: true});
});

// GET all trips of the given vin and date
router.get('/getTrips/:date/:vin', authenticationMiddleware(), function(req, res) {
  var date = req.params.date;
  var vin = req.params.vin;
  if(req.params.date === "undefined") {
    var today = new Date();
    var dd = today.getDate();
    var mm = today.getMonth() + 1; // January is 0!
    var yyyy = today.getFullYear();
    if(dd < 10) {
        dd = '0'+ dd
    }
    if(mm < 10) {
        mm = '0'+ mm
    }
    date = mm + '-' + dd + '-' + yyyy;
  } 
  var db = require('../db.js');
  db.query('SELECT filename, starttime, totalKM, vin FROM data WHERE date=?', [date], function(err, results, fields) {
    if(err) throw err;
    var data = [];
    for(var i = 0; i < results.length; i++) {
      if(bcrypt.compareSync(vin, results[i].vin)) {
        data.push({
          filename: results[i].filename,
          starttime: results[i].starttime,
          totalKM: results[i].totalKM
        })
      }
    }
    res.send(data);
  });
});

// GET login page
router.get('/login', function(req, res, next) {
  if(req.isAuthenticated()) {
    res.redirect('/dashboard')
  }
  res.render('login', { title: 'Login', login: true });
});

// Handle POST of login page
// Use passport.authenticate with custom callbacks to authenticate the user
// See the official passport documentation: http://www.passportjs.org/docs/authenticate/ 
router.post('/login', function(req, res, next) {
  passport.authenticate('local', function(err, user, info) {
    if (err) { return next(err);}
    if (!user) { 
      // See the possible messages in ../app.js
      console.log(info.message);
      req.data = info.message;
      req.id = info.user_id;
      req.email = info.email;
      return next(); 
    }
    req.logIn(user, function(err) {
      if (err) { return next(err); }
      return res.redirect('/dashboard');
    });
  })(req, res, next);
}, function(req, res, next) {
  var error = [{
    msg: req.data
  }]
  if (req.data === 'Confirm your email!') {
    mailer(req.id, req.email, "confirmation");
  }
  console.log(`Login errors: ${JSON.stringify(error)}`);
  res.render('login', { 
    title: 'Login failed',
    errors: error,
    login: true
  });
});

// GET page to request a password reset
router.get('/resetpw', function(req, res, next) {
  res.render('resetpw', { title: 'Reset your password' });
});

// Handle POST of reset password request page
router.post('/resetpw', function(req, res, next) {
  var db = require('../db.js');
  db.query('SELECT id, email FROM users WHERE username = ?', [req.body.username], function(error, results, fields) {    // use ? so that you can't hack the server with unwanted inputs
    if(error) {
      var error = [{
        msg: 'Username doesn\'t exists.'
      }]
      console.log(`errors: ${JSON.stringify(error)}`);
      res.render('resetpw', { 
        title: 'Resetting password failed!',
        errors: error
      });
    } else if (results[0].email === req.body.email) {
      mailer(results[0].id, req.body.email, "resetpw")
      res.redirect('/login');
    } else {
      var error = [{
        msg: 'Email is wrong.'
      }]
      console.log(results[0].username);
      console.log(`errors: ${JSON.stringify(error)}`);
      res.render('resetpw', { 
        title: 'Resetting password failed!',
        errors: error
      });
    }
  });
});

// GET page to reset the password
router.get('/resetpw:token', function(req, res, next) {
  res.render('resetpw_confirmed', { 
    title: 'Reset your password',
    token: req.params.token
  });
});

// Handle POST of reset password page
router.post('/resetpw_confirmed:token', function(req, res, next) {
  req.checkBody('password', 'Password must be between 8-100 characters long.').len(8, 100);
  req.checkBody("password", "Password must include one lowercase character, one uppercase character, a number, and a special character.").matches(/^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?!.* )(?=.*[^a-zA-Z0-9]).{8,}$/, "i");
  req.checkBody('passwordMatch', 'Password must be between 8-100 characters long.').len(8, 100);
  req.checkBody('passwordMatch', 'Passwords do not match, please try again.').equals(req.body.password);
       
  const errors = req.validationErrors();
  
  if(errors) {
    // if errors occur they should be outputted on the register page
    console.log(`errors: ${JSON.stringify(errors)}`);
    res.render(`resetpw${req.params.token}`, { 
      title: 'Resetting failed',
      errors: errors
    });
  } else {
    var id = jwt.verify(req.params.token, process.env.MAIL_SECRET);
    console.log(id);
    const password = req.body.password;
    // connect to a MySQL server 
    var db = require('../db.js');
    // hash the password and save the hash into the MySQL server
    bcrypt.hash(password, saltRounds, function(err, hash) {
      db.query('UPDATE users SET confirmed = 1, password = ? WHERE id = ?', [hash, id.user], function(error, results, fields) {    // use ? so that you can't hack the server with unwanted inputs
        if(error) {
          console.log(`errors: ${JSON.stringify(error)}`);
          res.render(`resetpw${req.params.token}`, { 
            title: 'Resetting failed',
            errors: errors
          });
        } else {
            res.redirect('/login');
        }
      });
    });
  }
});

// Destroy session via logout button
router.get('/logout', function(req, res, next) {
  req.logout()
  req.session.destroy(() => {
    res.clearCookie('connect.sid')
    res.redirect('/')
  })
});

// GET register page
router.get('/register', function(req, res, next) {
  if(req.isAuthenticated()) {
    res.redirect('/dashboard')
  }
  res.render('register', { title: 'Registration', register: true });
});

// handle POST of register page
router.post('/register', function(req, res, next) {
  // check the registration input with express-validator
  req.checkBody('username', 'Username field cannot be empty.').notEmpty();
  req.checkBody('username', 'Username must be between 4-15 characters long.').len(4, 15);
  req.checkBody('email', 'The email you entered is invalid, please try again.').isEmail();
  req.checkBody('email', 'Email address must be between 4-100 characters long, please try again.').len(4, 100);
  req.checkBody('password', 'Password must be between 8-100 characters long.').len(8, 100);
  req.checkBody("password", "Password must include one lowercase character, one uppercase character, a number, and a special character.").matches(/^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?!.* )(?=.*[^a-zA-Z0-9]).{8,}$/, "i");
  req.checkBody('passwordMatch', 'Password must be between 8-100 characters long.').len(8, 100);
  req.checkBody('passwordMatch', 'Passwords do not match, please try again.').equals(req.body.password);
       
  const errors = req.validationErrors();
  
  if(errors) {
    // if errors occur they should be outputted on the register page
    console.log(`errors: ${JSON.stringify(errors)}`);
    res.render('register', { 
      title: 'Registration failed',
      errors: errors
    });
  } else {
    const username = req.body.username;
    const email = req.body.email;
    const password = req.body.password;
    // connect to a MySQL server 
    var db = require('../db.js');
    // hash the password and save the hash into the MySQL server
    bcrypt.hash(password, saltRounds, function(err, hash) {
      db.query('INSERT INTO users (username, email, password) VALUES (?, ?, ?)', [username, email, hash], function(error, results, fields) {    // use ? so that you can't hack the server with unwanted inputs
        if(error) {
          console.log(`errors: ${JSON.stringify(error)}`);
          var error = [{
            msg: 'Username already exists.'
          }]
          console.log(`errors: ${JSON.stringify(error)}`);
          res.render('register', { 
            title: 'Registration failed',
            errors: error
          });
        } else {
          // login in the user with the user_id that was automatically created by MySQL
          db.query('SELECT LAST_INSERT_ID() as user_id', function(error, results, fields) {
            if(error) throw error;
            const user_id = results[0].user_id;
            console.log(user_id);
            // login (passport) uses serialization-function
            /*req.login(user_id, function(err) {
              res.redirect('/');
            });*/
            console.log(process.env.MAIL_PASSWORD)
            mailer(user_id, req.body.email, "confirmation")
            res.redirect('/login');
          });
        }
      });
    });
  } 
});

// save the user_id as a session information
passport.serializeUser(function(user_id, done) {
  done(null, user_id);
});
// read all session information
passport.deserializeUser(function(user_id, done) {
  done(null, user_id);
});
// check whether the user is authenticated, if not redirect him to the login page
function authenticationMiddleware() {
  return (req, res, next) => {
    console.log(`req.session.passport.user: ${JSON.stringify(req.session.passport)}`);
    if (req.isAuthenticated()) return next();
    res.redirect('/login');
  }
}

module.exports = router;
