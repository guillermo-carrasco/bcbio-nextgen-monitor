// Custom JS methods and utils for bcbio-nextgen-monitor

// Viz/graphviz utils
function update_flowchart() {
    $.getJSON("/api/graph", function(data){
        // Fill in graph data
        var fc_viz = Viz(data['graph_data'], options={ format:"svg", engine:"dot" });
        var parser = new DOMParser();
        var fc_svg = parser.parseFromString(fc_viz, "image/svg+xml").children[0];
        fc_svg.style.display = "block";
        fc_svg.style.margin = "auto";
        var div_graph = $('#progress_graph')[0];
        $('#progress_graph svg').remove()
        div_graph.appendChild(fc_svg);
    });
}

function update_table() {
    $.getJSON("/api/progress_table", function(data){
        for (step in data['table_data']) {
            add_table_row(data['table_data'][step]);
        }
    });
}

function update_log_message() {
    $.getJSON("/api/last_message", function(message){
        var panel = $("#panel-message");
        if (panel.length){
            panel = $("#panel-message")[0];
            panel.textContent = message['line'];
            if (message['step'] == 'error') {
                $("#panel-message").css('background-color', 'rgba(231, 76, 60, 0.61)')
            }
        }
    });
}

function update_progress_bar(){

    var pr = $("#progress_bar")[0];
    $.getJSON("/api/progress_table", function(data){
        var steps = data['table_data'];
        var portion_bar = '<div class="progress-bar" style="width: {percent}; background: {bg}" title="{title} ({pc}%)" data-toggle="tooltip" data-placement="top" id="{id}"></div>';
        if (steps.length == 1) {
            pr.innerHTML = portion_bar.allReplace({'{percent}': '100%', '{title}': steps[0]['step'], '{pc}': '100',
                                                   '{id}': steps[0]['step'].replace(' ', '_'), '{bg}': COLORS[0]});
        }
        else if (steps.length > 1) {
            var times = new Array();
            for (var i = 1; i < steps.length; i++) {
                times.push(moment(steps[i]['when']).diff(steps[i-1]['when'], 'seconds'));
            }
            var total_time = moment(steps[steps.length - 1]['when']).diff(moment(steps[0]['when']), 'seconds');
            pr.innerHTML = ''
            for (var i = 0; i < steps.length; i++) {
                var percent;
                total_time == 0 ? percent = 100 : percent = (times[i]/total_time) * 100;
                pr.innerHTML += portion_bar.allReplace({'{percent}': percent + '%', '{title}': steps[i]['step'], '{pc}': parseFloat(percent).toFixed(2),
                                                        '{id}': steps[i]['step'].replace(' ', '_'), '{bg}': COLORS[i%N_COLORS]});
            }
        }
        $('[data-toggle="tooltip"]').tooltip();
    });
}

function add_table_row(data) {
    var t = $("#progress_table")[0];
    // Set last label as finished
    var table_rows = $("#progress_table tr")
    if (table_rows.length) {
        var last_row = table_rows[table_rows.length - 1]
        var label = last_row.getElementsByClassName('label')[0]
        label.classList.remove('label-default')
        label.classList.add('label-success')
        label.textContent = 'finished';
    }

    var tr = document.createElement('tr');
    // Step column
    var td = document.createElement('td')
    td.textContent = data['step'].replace('_', ' ')
    tr.appendChild(td);
    // timestamp column
    var td = document.createElement('td')
    var when = moment(data['when']);
    td.textContent = when.calendar();
    tr.appendChild(td);
    // Status column
    var td = document.createElement('td')
    var label = document.createElement('span');
    label.classList.add('label');

    if (data['step'] == 'finished') {
        label.textContent = 'finished';
        label.classList.add('label-success');
        document.getElementById('summary-div').setAttribute('data-toggle', 'modal')
        document.getElementById("summary-button").innerHTML = 'Analysis finished. Click to see a summary';
        document.getElementById("summary-button").classList.remove('disabled');
        create_summary();
    }
    else {
        label.textContent = 'running';
        label.classList.add('label-default');
    }
    td.appendChild(label);
    tr.appendChild(td);
    t.appendChild(tr);
}


function create_summary() {
    $.getJSON('/api/summary', function(summary_data){
        // Create table for times summary
        var times_summary = summary_data['times_summary'];
        var total_time = 0;
        $.each(times_summary, function(intex, step){
            total_time += step[1];
            var tr = $('<tr></tr>')
            tr.append($('<td></td>').text(step[0]));
            tr.append($('<td></td>').text(moment.duration(step[1], 'seconds').humanize()));
            $("#times-summary-table-body").append(tr);
        });
        //Total analysis time
        $("#analysis-time").text(moment.duration(total_time, 'seconds').humanize());
    });
}

//SSE messages subscriptions
var source = new EventSource("/subscribe");

source.addEventListener('message', function(e) {
  var data = JSON.parse(e.data);
  // Update flowchart, table and progress bar if its a new step
  if (data.hasOwnProperty('when')) {
    update_flowchart();
    add_table_row(data);
    update_progress_bar();
  }
  if (data['step'] == 'error') {
      // Set last label as error
      var table_rows = $("#progress_table tr")
      if (table_rows.length) {
          var last_row = table_rows[table_rows.length - 1]
          var label = last_row.getElementsByClassName('label')[0]
          label.classList.remove('label-default')
          label.classList.add('label-danger')
          label.textContent = 'Error';
      }
  }
  // Update log messages panel
  update_log_message();
}, false);

source.addEventListener('open', function(e) {
  console.log("Connection with bcbio-monitor server opened.")
}, false);

source.addEventListener('error', function(e) {
  if (e.readyState == EventSource.CLOSED) {
    console.log("Connection with bcbio-monitor server was closed.")
  }
}, false);


// Replace several strings on the same call
String.prototype.allReplace = function(obj) {
    var retStr = this;
    for (var x in obj) {
        retStr = retStr.replace(new RegExp(x, 'g'), obj[x]);
    }
    return retStr;
};

// On start...
$(document).ready(function(){

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

    update_flowchart();
    update_table();
    update_progress_bar();
    update_log_message();
});
