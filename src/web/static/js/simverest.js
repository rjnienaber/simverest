function VarnishServerController($defer) {
    var self = this;
    this.servers = [];
    this.current_server = '';
    this.backends = [];
    this.process = [];
    this.varnishstats = [];
    this.timestamp = '';
    
    this.change_server = function() {
        self.current_server = this.server;
        set_title(this.server);
        self.backends = [];
        self.process = [];
        self.varnishstats = [];
        
        //graphs
        sparkMap = {};
        chartMap = {};
        counter = 1;
        colourCounter = 1;
        $.plot($("#graph1"), [], {});
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
    }
    
    this.getStats = function() {
        matches = /#.*/.exec(window.location.href);
        if (matches && matches.length > 0) {
            hash_server = matches[0].substr(1);
            if (hash_server != self.current_server)
                self.current_server = hash_server;
        }
    
        var statsUrl = "api/server/" + self.current_server;
        $.getJSON(statsUrl, self.updateServerInfo);
        
        $defer(function() { self.getStats(); }, 1000);
    }
    
    //start retrieving data
    $.getJSON("api/servers",
        function(data) {
            if (!data.servers || data.servers.length == 0)
                return;
                
            data.servers.sort();
            self.servers = data.servers;
                
            self.current_server = data.servers[0];

            self.getStats();
            set_title(self.current_server);
        });
        
    $(function() {
        $(window).hashchange(function(){
            if (location.hash == '' && self.servers.length == 0)
                return;
            
            var server = location.hash != '' ? location.hash.substr(1) : self.servers[0];
            var thisValue = {server: server};
                
            self.change_server.call(thisValue);
        });
        $(window).hashchange();
    });
}

function set_title(server_name) {
    document.title = 'Simverest - ' + server_name
}

var initialized = false;
function check_load_complete() {
    if (!initialized && $('#backends > tbody > tr').html().trim() != "") {
        initialized = true;
        $('#loading_container').hide();
        $('.container, .nav-collapse').fadeIn(500);
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

