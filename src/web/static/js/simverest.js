function VarnishServerController() {
    var self = this;
    this.backends = []
    this.process = []
    this.varnishstats = []
    this.timestamp = ''
    
    this.getHealthLabel = function(index) {
        return this.backends[index].state == 'healthy' ? "success" : "important";
    }
    
    this.updateServerInfo = function(data) {
        check_load_complete();
        
        self.backends = data.backends;
        updateFaviconHealthCount(data.backends);
        
        var process_values = []
        var addValue = function(name, value, description) {
            process_values.push({description: description, value: value, name: name})
        }
        addValue('cpu', data.process.cpu.toFixed(1), 'CPU (%)');
        addValue('memory', data.process.memory.toFixed(1), 'Memory (%)');
        addValue('reservedmem_mb', data.process.reservedmem_mb, 'Reserved Memory (Mb)');
        addValue('virtualmem_mb', data.process.virtualmem_mb, 'Virtual Memory (Mb)');
        
        self.process = process_values;
        self.timestamp = data.timestamp;
        self.varnishstats = data.varnishstats;
        
        drawSparkLines(process_values.concat(data.varnishstats))
        drawGraph(data.varnishstats);
        
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

var initialized = false;
function check_load_complete() {
    if (!initialized && $('#backends > tbody > tr').html().trim() != "") {
        initialized = true;
        $('#loading_container').hide();
        $('.container').fadeIn(500);
    }
}

function updateFaviconHealthCount(backends) {
    var errorCount = 0;
    $(backends).each(function(i, backend) {
        if (backend.state == 'sick')
            errorCount++;
    });
    
    Tinycon.setBubble(errorCount);
    if (errorCount == 0)
        Tinycon.reset();
}

var sparkMap = {};
function drawSparkLines(values) {
    $(values).each(function (index, data) {
        var sparkValues = sparkMap[data.name] || []

        if(sparkValues.length == 20)
            sparkValues.splice(0, 1);
        
        sparkValues.push(data.value);
        sparkMap[data.name] = sparkValues;
    });
    
    $('.sparkline').each(function() {
        var name = $(this).parent().parent().attr('id')
        $(this).sparkline(sparkMap[name], { width: sparkMap[name].length * 4 });
    });
}

var chartMap = {};
var counter = 1;
var colourCounter = 1;

function drawGraph(varnishstats){
    var values;
    for (index in varnishstats) {
        values = varnishstats[index];
        if (values.name == 'client_conn')
            break;
    }
    
    var name = values.name;
    if (chartMap[name] == null)
        chartMap[name] = {label: name, data:[], color: colourCounter++};
    
    var chartData = chartMap[name].data;
    if (chartData.length == 120)
        chartData.splice(0, 1);

    chartData.push([counter++, values.value]);

    $.plot($("#graph1"), [chartMap[name]], {
        yaxis: { min: 0 },
        xaxis: { tickDecimals: 0 }
    });
}