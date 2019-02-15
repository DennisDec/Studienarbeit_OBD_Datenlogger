var now = Date.now();

$('[data-toggle="datepicker"]').datepicker({
  filter: function(date, view) {
    if (date.getDay() === 0 && view === 'day') {
      return false; // Disable all Sundays, but still leave months/years, whose first day is a Sunday, enabled.
    }
  }
});