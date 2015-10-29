// Custom JS methods and utils for bcbio-nextgen-monitor

// Viz/graphviz utils

function update_flowchart() {
    $.getJSON("/api/graph", function(data){
        var fc_viz = Viz(data['graph_data'], options={ format:"svg", engine:"dot" });
        var parser = new DOMParser();
        var fc_svg = parser.parseFromString(fc_viz, "image/svg+xml");
        var div_graph = $('#progress_graph')[0];
        div_graph.appendChild(fc_svg.children[0]);
    });
}

$(document).ready(function(){
    update_flowchart();
});
