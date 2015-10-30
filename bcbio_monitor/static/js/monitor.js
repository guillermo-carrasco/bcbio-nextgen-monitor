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
        div_graph.appendChild(fc_svg);

        // Fill in timing table data
        var t = $("#progress_table")[0];
        $("#progress_table tr").remove()
            for (var elem in data['table_data']) {
                $.each(data['table_data'][elem], function(step, status) {
                    var tr = document.createElement('tr');
                    // Step column
                    var td = document.createElement('td')
                    td.textContent = step.replace('_', ' ')
                    tr.appendChild(td);
                    // timestamp column
                    var td = document.createElement('td')
                    td.textContent = status['timestamp'];
                    tr.appendChild(td);
                    // Status column
                    var td = document.createElement('td')
                    var label = document.createElement('span');
                    label.classList.add('label');
                    if (status['status'] == 'finished') {
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
                });
            }
    });
}

//SSE messages subscriptions
var evtSrc = new EventSource("/subscribe");

evtSrc.onmessage = function(e) {
    console.log(e.data);
};


// On start...
$(document).ready(function(){
    update_flowchart();
});
