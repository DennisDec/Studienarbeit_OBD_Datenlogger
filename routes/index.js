var express = require('express');
var router = express.Router();

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

module.exports = router;
