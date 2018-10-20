var express = require('express');
var router = express.Router();
var expressValidator = require('express-validator');
const bcrypt = require('bcrypt');


// GET home page
router.get('/', function(req, res) {
  res.render('home', { title: 'Home' });
});

// GET profile page
router.get('/profile', function(req, res, next) {
  res.render('profile', { title: 'Profile' });
});

// GET login page
router.get('/login', function(req, res, next) {
  res.render('login', { title: 'Login' });
});

// GET register page
router.get('/register', function(req, res, next) {
  res.render('register', { title: 'Registration' });
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
  req.checkBody('username', 'Username already exists.').usernameExists(req.body.username);
  
  //const errors = req.validationErrors();
  // due to the custom check async errors can occur
  req.asyncValidationErrors().then(function() {
    next();
  }).catch(function(errors) {
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
      const db = require('../db.js');
      // hash the password and save the hash into the MySQL server
      bcrypt.hash(password, saltRounds, function(err, hash) {
        db.query('INSERT INTO users (username, email, password) VALUES (?, ?, ?)', [username, email, hash], function(error, results, fields) {    // use ? so that you can't hack the server with unwanted inputs
          if(error) throw error;
          res.render('register', { title: 'Registration complete' });
        });
      });
    } 
  });
});

module.exports = router;
