<html>
    <head>
        <meta http-equiv="refresh" content="1"></meta>
        <title>Varnish Status</title>
        <style>
            #status, #process, #stat {
                border-collapse: collapse;
                border-style: solid;
                border-width: 1px;
            }
            #status td, #status tr, #status th{
                border: 1px solid black 
            }

            .lastchanged {
                width: 170px; 
                text-align: right
            } 
        </style>
    </head>
    <body>
        <h1>Varnish Monitor: {{name}}</h1>
        <span>Last Update: {{last_update}}</span>
		<p>
			<table id="status">
				<tr>
					<th>Name</th>
					<th>Status</th>
					<th class="lastchanged">Last Changed</th>
				</tr>
				%for backend in sorted(backends, key=lambda x: x['name']):
				<tr>
					<td>{{backend['name']}}</td>
					<td>{{backend['state']}}</td>
					<td class="lastchanged">{{backend['last_change']}}</td>
				</tr>
				%end
			</table>
		</p>
		<p>
			<table id="process">
				<tr>
					<th>Name</th>
					<th>Value</th>
				</tr>
				%for name in sorted(process):
				<tr>
					<td>{{name}}</td>
					<td>{{process[name]}}</td>
				</tr>
				%end
			</table>
		</p>
		<p>
			<table id="stat">
				<tr>
					<th>Name</th>
					<th>Status</th>
					<th class="description">Description</th>
				</tr>
				%for stat in varnish:
				<tr>
					<td>{{stat['name']}}</td>
					<td>{{"{0:.2f}".format(stat['value'])}}</td>
					<td class="description">{{stat['description']}}</td>
				</tr>
				%end
			</table>
		</p>
    </body>
</html>
