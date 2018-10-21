var express = require('express');
var path = require('path');
var favicon = require('serve-favicon');
var logger = require('morgan');
var cookieParser = require('cookie-parser');
var bodyParser = require('body-parser');
var expressValidator = require('express-validator');

var session = require('express-session');
var passport = require('passport');
var LocalStrategy = require('passport-local').Strategy;
var MySQLStore = require('express-mysql-session')(session);
var bcrypt = require('bcrypt');

var index = require('./routes/index');
var users = require('./routes/users');

var app = express();

require('dotenv').config();         // needed to use process.env

// view engine setup
app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'hbs');

// uncomment after placing your favicon in /public
//app.use(favicon(path.join(__dirname, 'public', 'favicon.ico')));
app.use(logger('dev'));
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: false }));

// Use Express Validator
app.use(expressValidator({ 
  customValidators: {                           // create custom validators
    usernameExists: function(username) {        // create a validator with the name of 'usernameExists' and make it a function
      return new Promise(function(resolve, reject) {
        const db = require('./db.js');
        db.query('SELECT id FROM users WHERE username = ?', [username], function(err, results, fields) {
          if (err) reject(err);
          if(results.length === 0) {            
            resolve();
          } else {
            reject();
          }
        })
      })
    }
  }
}));

app.use(cookieParser());
//app.use(express.static(path.join(__dirname, 'public')));

// set up a session and save it in MySQL when the user is authenticated
var options = {
  host: process.env.DB_HOST,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  database : process.env.DB_NAME
};
// saves the session information in MySQL
var sessionStore = new MySQLStore(options);

app.use(session({
  secret: 'aiuwhdhwoawd',   
  store: sessionStore,
  resave: 'false',          // doesn't resave the session information after every refresh
  saveUninitialized: false  // saves session information only if user is initialized
}));

// use passport
app.use(passport.initialize());
app.use(passport.session());

// every route is now able to see whether the user is authenticated 
app.use(function(req, res, next) {
  res.locals.isAuthenticated = req.isAuthenticated();   
  next();
});

app.use('/', index);
app.use('/users', users);

// set up the strategy for passport
// therefor the input password has to be compared to the saved password
passport.use(new LocalStrategy(
  function(username, password, done) {
    console.log(username);
    const db = require('./db.js');
    db.query('SELECT id, password FROM users WHERE username = ?', [username], function(err, results, fields) {
      if (err) done(err);
      if(results.length === 0) {    
        done(null, false);
      } else {
        const hash = results[0].password.toString();
        bcrypt.compare(password, hash, function(err, response) {
          if (response === true) {
            return done(null, {user_id: results[0].id});
          } else {
            return done(null, false);
          }
        });
      }
    });  
  }
));

// catch 404 and forward to error handler
app.use(function(req, res, next) {
  var err = new Error('Not Found');
  err.status = 404;
  next(err);
});

// error handler
app.use(function(err, req, res, next) {
  // set locals, only providing error in development
  res.locals.message = err.message;
  res.locals.error = req.app.get('env') === 'development' ? err : {};

  // render the error page
  res.status(err.status || 500);
  res.render('error');
});


// Handlebars default config
const hbs = require('hbs');
const fs = require('fs');

const partialsDir = __dirname + '/views/partials';

const filenames = fs.readdirSync(partialsDir);

filenames.forEach(function (filename) {
  const matches = /^([^.]+).hbs$/.exec(filename);
  if (!matches) {
    return;
  }
  const name = matches[1];
  const template = fs.readFileSync(partialsDir + '/' + filename, 'utf8');
  hbs.registerPartial(name, template);
});

hbs.registerHelper('json', function(context) {
    return JSON.stringify(context, null, 2);
});

module.exports = app;
