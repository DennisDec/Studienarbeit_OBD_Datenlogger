var express = require('express');
var router = express.Router();
var expressValidator = require('express-validator');
var passport = require('passport');
const bcrypt = require('bcrypt');
var nodemailer = require('nodemailer');
var fs = require('fs');

var mailer = require('../mailer.js');
var jwt = require('jsonwebtoken');

const saltRounds = 10;

// GET home page
router.get('/', function(req, res) {
  res.render('home', { title: 'Home', home: true });
});

router.get('/confirmation/:token', function(req, res) {
  console.log(req.params.token);
  var id = jwt.verify(req.params.token, process.env.MAIL_SECRET);
  console.log(id);
  var db = require('../db.js');
  db.query('UPDATE users SET confirmed = 1 WHERE id = ?', [id.user], function(err, results, fields) {
    if(err) throw err;
  });
  res.redirect('/login');
});

// GET dashboard page; only accessable for authenticated users
router.get('/dashboard', authenticationMiddleware(), function(req, res, next) {
  // get GPS-data from the MySQL-server and save it into a json-file 
  var db = require('../db.js');
  db.query('SELECT * FROM gpsdata', function(err, results, fields) {
    if(err) throw err;
    fs.writeFile('src/maps/markers.json', JSON.stringify(results), function (err) {
      if (err) throw err;
      console.log('GPS-data saved');
    });
  });
  db.query('SELECT * FROM importobd', function(err, results, fields) {
    if(err) throw err;
    fs.writeFile('src/obd/data.json', JSON.stringify(results), function (err) {
      if (err) throw err;
      console.log('OBD-data saved');
    });
  });
  res.render('dashboard', { title: 'Dashboard', dashboard: true });
});

// GET login page
router.get('/login', function(req, res, next) {
  res.render('login', { title: 'Login', login: true });
});
// handle POST of login page; use passport to authenticate the user
/*router.post('/login', passport.authenticate('local', {
  successRedirect: '/dashboard',
  failureRedirect: '/loginFail'
}));*/
router.post('/login', function(req, res, next) {
  passport.authenticate('local', function(err, user, info) {
    if (err) { return next(err);}
    if (!user) { 
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
  console.log(`errors: ${JSON.stringify(error)}`);
  res.render('login', { 
    title: 'Login failed',
    errors: error,
    login: true
  });
});
// after unsuccessful login head to route /loginFail and show error message
/*router.get('/loginFail', function(req, res, next) {
  var error = [{
    msg: 'Incorrect username or password.'
  }]
  console.log(`errors: ${JSON.stringify(error)}`);
  res.render('login', { 
    title: 'Login failed',
    errors: error,
    login: true
  });
});*/
router.get('/resetpw', function(req, res, next) {
  res.render('resetpw', { title: 'Reset your password' });
});

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

router.get('/resetpw:token', function(req, res, next) {
  res.render('resetpw_confirmed', { 
    title: 'Reset your password',
    token: req.params.token
  });
});

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
