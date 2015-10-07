// Initialize mermeid stuff

var mermaid_config = {
    startOnLoad: true,
    flowchart:  {
        useMaxWidth:true,
        htmlLabels:true,
        logLevel: 1,
        heigh: 1000
    }
}

function callback_null(){
    // Does nothing
}

mermaid.initialize(mermaid_config);
