var backendURL = "api/server/DC-PP-VRN1/backends?callback=?";
var statsURL = "api/server/DC-PP-VRN1/stats?callback=?";
var timer;
var sparkMap = {};
var chartMap = {};
var counter = 1;
var colourCounter = 1;

$(document).ready(function (){
    execute();
});

function execute(){
    getBackends();
    getStats();

    counter++;

    timer=setTimeout("execute()",1000);
}

function getBackends(){
    $.getJSON(backendURL,
        function(data) {
            $.each(data.backends, function(i,backend){
                var name = backend.name;

                var table = $('#backends');
                var row = table.find('#'+name);

                if (row.html() == null){
                    createServerStatusRow(table, name);
                    updateServerStatusRow(table.find('#'+name), backend);
                }else{
                    updateServerStatusRow(row, backend);
                }
            });
        });
}

function getStats(){
    $.getJSON(statsURL,
        function(data) {
            updateTimestamp(data.timestamp);
            updateProcess(data.process);
            updateStats(data.varnishstats);
        });
}


function updateDataPoints(row, name, info){
    if(sparkMap[name] == null){
        sparkMap[name] = [];
    }

    if(sparkMap[name].length == 20){
        for(var i = 0; i < 20; i ++){
            sparkMap[name][i] = sparkMap[name][i+1];
        }
        sparkMap[name].pop();
    }

    sparkMap[name].push(info);

    if(chartMap[name] == null){
        chartMap[name] = {'label':name, 'data':[], 'color': colourCounter++};
    }

    if(chartMap[name].data.length == 120){
        for(var i = 0; i < 120; i ++){
            chartMap[name].data[i] = chartMap[name].data[i+1];
        }
        chartMap[name].data.pop();
    }

    chartMap[name].data.push([counter,info]);

    drawSparklines(row, name);
    drawGraph();

}

function updateTimestamp(timestamp){
    $('#timeLastUpdated').html(timestamp);
}

function createServerStatusRow(table, name){
    table.find('tbody')
        .append($('<tr id="'+name+'">')
            .append($('<td>')
                .text(name)
            )
            .append($('<td class="lastchanged">')
            )
            .append($('<td class="health">')
                .append('<span class="label label-success">')
            )
            .append($('<td>')
                .append('<i class="icon-resize-full">')
            )
        );
}

function updateServerStatusRow(row, backendData){
    row.find('.lastchanged').html(backendData.timestamp);

    if(backendData.state == "healthy"){
        row.find('.health').find('span').html("Healthy");
        row.find('.health').find('span').removeClass("label-important");
        row.find('.health').find('span').addClass("label-success");
    }else{
        row.find('.health').find('span').html("Failure");
        row.find('.health').find('span').removeClass("label-success");
        row.find('.health').find('span').addClass("label-important");
    }
}

function updateProcess(processInfo){

    $.each(processInfo, function(key, val) {
        var table = $('#process');
        var row = table.find('#'+key);

        if (row.html() == null){
            createProcessRow(table, key);
            updateProcessRow(table.find('#'+key), key, val);
        }else{
            updateProcessRow(row, key, val);
        }
    });
}

function createProcessRow(table, name){
    table.find('tbody')
        .append($('<tr id="'+name+'">')
            .append($('<td>')
                .text(name)
            )
            .append($('<td class="processValue">')
            )
            .append($('<td>')
                .append('<i class="icon-resize-full">')
            )
            .append($('<td class="spark_cell">')
            )
        );
}

function updateProcessRow(row, name, info){
    row.find('.processValue').html(info);

    updateDataPoints(row, name, info);
}

function updateStats(statsInfo){
    $.each(statsInfo, function(i,info){
        var name = info.name;

        var table = $('#stats');
        var row = table.find('#'+name);

        if (row.html() == null){
            createStatsRow(table, name);
            updateStatsRow(table.find('#'+name), name, info);
        }else{
            updateStatsRow(row, name, info);
        }
    });
}

function createStatsRow(table, name){
    table.find('tbody')
        .append($('<tr id="'+name+'">')
            .append($('<td class="statDescription">')
            )
            .append($('<td class="statStatus">')
            )
            .append($('<td>')
                .append('<i class="icon-resize-full">')
            )
            .append($('<td class="spark_cell">')
            )
        );
}

function updateStatsRow(row, name, info){
    row.find('.statStatus').html(info.value.toFixed(2));
    row.find('.statDescription').html(info.description);

    updateDataPoints(row, name, info.value.toFixed(2))
}

function drawSparklines(row, name){

    if(row.find('.spark_cell').find('.sparkline').html() == null){
        row.find('.spark_cell').append($('<span class="sparkline" id="spark_'+name+'">'));
    }

    $('#spark_'+name).sparkline(sparkMap[name], { width: sparkMap[name].length*4 });
}



function drawGraph(){

    var data = [];

    if(chartMap['client_conn'] != null){
        data.push(chartMap['client_conn']);
    }

    $.plot($("#graph1"), data, {
        yaxis: { min: 0 },
        xaxis: { tickDecimals: 0 }
    });
}


