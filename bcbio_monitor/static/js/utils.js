// Format locale
moment.locale('en', {
  calendar : {
    lastDay : '[Yesterday at] LT',
      sameDay : '[Today at] LT',
      nextDay : '[Tomorrow at] LT',
      lastWeek : '[last] dddd [at] LT',
      nextWeek : 'dddd [at] LT',
      sameElse : 'L'
  }
});

moment.locale('en', {
    longDateFormat : {
        LT: "H:mm ",
        LTS: "h:mm:ss A",
        L: "YYYY MMM Do, H:mm",
        l: "M/D/YYYY",
        LL: "MMMM Do YYYY",
        ll: "MMM D YYYY",
        LLL: "MMMM Do YYYY LT",
        lll: "MMM D YYYY LT",
        LLLL: "dddd, MMMM Do YYYY LT",
        llll: "ddd, MMM D YYYY LT"
    }
});

// Replace several strings on the same call
String.prototype.allReplace = function(obj) {
    var retStr = this;
    for (var x in obj) {
        retStr = retStr.replace(new RegExp(x, 'g'), obj[x]);
    }
    return retStr;
};

var COLORS = {
    0: '#1dd2af',
    1: '#3498db',
    2: '#9b59b6',
    3: '#7f8c8d',
    4: '#e67e22',
    5: '#2980b9',
    6: '#16a085',
    7: '#95a5a6',
    8: '#c0392b',
    9: '#d35400'
}

var N_COLORS = 10;
