var initialized = false;

function VarnishServerController() {
    self = this;
    this.backends = []
    this.process = []
    this.varnishstats = []
    this.timestamp = ''
    
    this.getHealthLabel = function(index) {
        return this.backends[index].state == 'healthy' ? "label-success" : "label-important";
    }
    
    this.updateServerInfo = function(data) {
        if (!initialized && $('#backends > tbody > tr').html().trim() != "") {
            initialized = true;
            $('body').fadeIn(500);
        }
        
        self.backends = data.backends;
        
        var process_values = []
        var addValue = function(name, value, description) {
            process_values.push({'description': description, 'value': value, 'name': name})
        }
        addValue('cpu', data.process.cpu.toFixed(1), 'CPU (%)');
        addValue('memory', data.process.memory.toFixed(1), 'Memory (%)');
        addValue('reservedmem_mb', data.process.reservedmem_mb, 'Reserved Memory (Mb)');
        addValue('virtualmem_mb', data.process.virtualmem_mb, 'Virtual Memory (Mb)');
        
        self.process = process_values;
        self.timestamp = data.timestamp;
        self.varnishstats = data.varnishstats;
        
		//update graph
        $(data.varnishstats).each(function (index, data) { updateDataPoints(data); });
        
        setTimeout("$('#update').click()", 1000);
    }
    
    this.getStats = function() {
        var statsUrl = "api/server/" + $('#serverName').val();
        $.getJSON(statsUrl, self.updateServerInfo);
    }
    
    $.getJSON("api/servers",
        function(data) {
            if (data.servers.length == 0)
                return;
            $('#serverName').val(data.servers[0]);
            self.getStats();
        });
}

$(function() {
    $('#sparkle_test').sparkline([1,2,3,4,5,4,3,2,1]);
});

var sparkMap = {};
var chartMap = {};
var counter = 1;
var colourCounter = 1;

function updateDataPoints(data){
    var name = data.name;
    var row = $('#' + name);
    if(sparkMap[name] == null){
        sparkMap[name] = [];
    }

    if(sparkMap[name].length == 20){
        for(var i = 0; i < 20; i ++){
            sparkMap[name][i] = sparkMap[name][i+1];
        }
        sparkMap[name].pop();
    }

    sparkMap[name].push(data.value);

    if(chartMap[name] == null){
        chartMap[name] = {'label':name, 'data':[], 'color': colourCounter++};
    }

    if(chartMap[name].data.length == 120){
        for(var i = 0; i < 120; i ++){
            chartMap[name].data[i] = chartMap[name].data[i+1];
        }
        chartMap[name].data.pop();
    }

    chartMap[name].data.push([counter, data.value]);

    drawSparklines(name);
    //drawGraph();

}
function drawSparklines(name){
	var selector = $('#spark_' + name);
	if (selector.length)
		selector.sparkline(sparkMap[name], { width: sparkMap[name].length * 4 });
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