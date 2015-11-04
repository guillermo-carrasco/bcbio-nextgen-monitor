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
    td.textContent = data['when'];
    tr.appendChild(td);
    // Status column
    var td = document.createElement('td')
    var label = document.createElement('span');
    label.classList.add('label');
    if (data['step'] == 'finished') {
        label.textContent = 'finished';
        label.classList.add('label-success');
    }
    else {
        label.textContent = 'running';
        label.classList.add('label-default');
    }
    td.appendChild(label);
    tr.appendChild(td);
    t.appendChild(tr);
}

//SSE messages subscriptions
var source = new EventSource("/subscribe");

source.addEventListener('message', function(e) {
  var data = JSON.parse(e.data);
  var panel = $("#panel-message");
  // Update flowchart and table if its a new step
  if (data.hasOwnProperty('when')) {
    update_flowchart();
    add_table_row(data);
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
  if (panel.length){
      panel = $("#panel-message")[0];
      panel.textContent = data['line'];
      if (data['step'] == 'error') {
          $("#panel-message").css('background-color', 'rgba(231, 76, 60, 0.61)')
      }
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



// On start...
$(document).ready(function(){
    update_flowchart();
    update_table();
});
