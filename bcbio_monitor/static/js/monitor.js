// Custom JS methods and utils for bcbio-nextgen-monitor

var CURRENT_RUN = "1";

function increment_run() {
  CURRENT_RUN = String(parseInt(CURRENT_RUN) + 1);
}


function update_flowchart(source) {
  var fc_viz = Viz(source, options={ format:"svg", engine:"dot" });
  var parser = new DOMParser();
  var fc_svg = parser.parseFromString(fc_viz, "image/svg+xml").children[0];
  fc_svg.style.display = "block";
  fc_svg.style.margin = "auto";
  $('#progress_graph svg').remove()
  $('#progress_graph').append(fc_svg);
}

function update_flowchart_for_run(run_id) {
  $.getJSON("/graph_source?run=" + run_id, function(data){
    update_flowchart(data['graph_source']);
  });
}


function update_progress_bar(steps) {
  var portion_bar = '<div class="progress-bar" style="width: {percent}; background: {bg}" title="{title}' +
                    ' ({pc}%)" data-toggle="tooltip" data-placement="top" id="{id}"></div>';
  if (steps.length == 1) {
    $("#progress_bar").append(portion_bar.allReplace({'{percent}': '100%', '{title}': steps[0]['step'],
                                                      '{pc}': '100', '{id}': steps[0]['step'].replace(' ', '_'),
                                                      '{bg}': COLORS[0]}));
  }
  else if (steps.length > 1) {
    var times = new Array();
    for (var i = 1; i < steps.length; i++) {
      times.push(moment(steps[i]['when']).diff(steps[i-1]['when'], 'seconds'));
    }
    var total_time = moment(steps[steps.length - 1]['when']).diff(moment(steps[0]['when']), 'seconds');
    $("#progress_bar").empty();
    for (var i = 0; i < steps.length; i++) {
      var percent;
      total_time == 0 ? percent = 100 : percent = (times[i]/total_time) * 100;
      $("#progress_bar").append(portion_bar.allReplace({'{percent}': percent + '%', '{title}': steps[i]['step'],
                                                        '{pc}': parseFloat(percent).toFixed(2), '{id}': steps[i]['step'].replace(' ', '_'),
                                                        '{bg}': COLORS[i%N_COLORS]}));
    }
  }
  $('[data-toggle="tooltip"]').tooltip();
}


function update_progress_bar_for_run(run_id) {
  $.getJSON("/steps?run=" + run_id, function(data){
    update_progress_bar(data['steps']);
  });
}


/*
 * If the method is called without parameters, it will update everything, otherwise it will only
 * update using the info in the parameter, which should be a log line.
 */
function update_info(new_line) {
  if (typeof(new_line) == 'object') {
    update_flowchart(new_line['graph_source']);
    add_table_row(new_line);
    update_progress_bar_for_run(CURRENT_RUN);
  }
  else if (typeof(new_line) == 'undefined') {
    $.getJSON("/runs_info", function(runs){
      runs = runs['data'].sort(compare);
      $.each(runs, function(i, run){
        if (i > 0) {
          create_new_run();
        }

        update_flowchart(run['graph_source']);

        // Update table
        $.each(run['steps'], function(s, step){
          if (!$("#" + step['step_id']).length) {
            add_table_row(step);
          }
        });

        update_progress_bar(run['steps']);
        update_log_message();
      });
    });
    $.getJSON("/status", function(status) {
      if (status['finished_reading']) {
        $("#loading_modal").modal('hide');
      }
    });
  }
}


function update_log_message() {
  $.getJSON("/last_message", function(message){
    var panel = $("#panel-message");
    if (panel.length){
      $("#panel-message").text(message['line']);
      if (message['step'] == 'error') {
        error();
      }
    }
  });
}

// Set up all frontend elements to show that there has been an error
function error() {
  if ($("#progress-table-run-" + CURRENT_RUN + " tr").length) {
    var label = $("#progress-table-run-" + CURRENT_RUN + " tr .label").last()[0];
    label.classList.remove('label-default');
    label.classList.add('label-danger');
    label.textContent = 'Error';
  }
  $("#summary-button").text('Analysis failed. No summary available');
  // Get current run (currently selected tab) and add an alert below
  var current_run = CURRENT_RUN;
  if (!$("#alert-run-" + current_run).length) {
    var error_text = "Error detected. Please go through the logs to determine the cause of the problem.";
    $("#table-run-" + current_run).after('<div class="alert alert-danger" role="alert" id="alert-run-' +
                                         current_run + '"> ' + error_text + '</div>');
  }
}


function add_table_row(data) {
  // Set last label as finished
  if ($("#progress-table-run-" + CURRENT_RUN + " tr").length) {
    var label = $("#progress-table-run-" + CURRENT_RUN + " tr .label").last()[0];
    label.classList.remove('label-default');
    label.classList.add('label-success');
    label.textContent = 'finished';;
  }

  var tr = document.createElement('tr');
  tr.setAttribute('id', data['step_id']);
  // Step column
  var td = document.createElement('td')
  td.textContent = data['step']
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
    $('#summary-div').attr('data-toggle', 'modal');
    $("#summary-button").text('Analysis finished. Click to see a summary');
    $("#summary-button").removeClass('disabled');

    // Create the summary and finally hide the loading modal
    create_summary();
    $("#loading_modal").modal('hide');
  }
  else {
    label.textContent = 'running';
    label.classList.add('label-default');
  }
  td.appendChild(label);
  tr.appendChild(td);
  $("#progress-table-run-" + CURRENT_RUN).append(tr);
}


function create_summary() {
  $.getJSON('/summary', function(summary_data){
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

// Creates holders for a new run
function create_new_run() {
  // Set as errored in the last Step
  error();
  increment_run();
  // Set current tab as inactive
  $('#runs_holder li[class="active"]').removeClass('active');
  $('#runs_holder_content div[class="tab-pane active"]').removeClass('active');
  // Create new tab
  var new_tab = '<li role="presentation" class="active" run="{cr}"><a href="#content-run-{cr}" aria-controls="content-run-{cr}" run="{cr}" role="tab" data-toggle="tab">Run #{cr}</a></li>'.replace(/{cr}/g, CURRENT_RUN);
  var new_tab_content = '<div role="tabpanel" class="tab-pane active" id="content-run-{cr}"></div>'.replace(/{cr}/g, CURRENT_RUN);
  $("#runs_holder").append(new_tab);
  $("#runs_holder_content").append(new_tab_content);

  // Create new table for the tab, copying the one from run 1
  var t2 = $("#table-run-1").clone();
  t2.attr('id', 'table-run-' + CURRENT_RUN);
  $("#content-run-" + CURRENT_RUN).append(t2);
  $("#table-run-" + CURRENT_RUN + " tbody").empty();
  $("#table-run-" + CURRENT_RUN + " tbody").attr('id', 'progress-table-run-' + CURRENT_RUN);
  setup_tabs();
}

//SSE messages subscriptions
var source = new EventSource("/subscribe");

source.addEventListener('message', function(e) {
  var data = JSON.parse(e.data);
  // If we finished loading the log file, close the loading modal
  if (data.hasOwnProperty('finished_reading')) {
    $("#loading_modal").modal('hide');
  }
  else {
    if (data['new_run']) {
      create_new_run();
    }
    // Update flowchart, table and progress bar if its a new step
    if (data.hasOwnProperty('when')) {
      update_info(data);
    }
    // Update log messages panel
    update_log_message();
  }
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

// Actibate tabs
function setup_tabs() {
  $('#runs_holder a').click(function (e) {
    e.preventDefault();
    $(this).tab('show')
  });
  // Update graph and progress bar for the selected tab
  $('a[data-toggle="tab"]').on('shown.bs.tab', function (e) {
    var run = e.currentTarget.getAttribute('run');
    update_flowchart_for_run(run);
    update_progress_bar_for_run(run);
  });
}

// On start...
$(document).ready(function(){

  $("#loading_modal").modal('show')

  update_info();
  update_log_message();
  setup_tabs();
});
