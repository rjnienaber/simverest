================== 
What is Simverest?
==================
Simverest acts as a simple dashboard for a `Varnish cache`__ server. It will provide you with information such as the current state of the backends, what the current processing load on the server is, and other useful stats provided by various Varnish_ programs.

Simverest uses common command line tools (e.g. grep, awk, top) to parse the output of these tools and provides a central location where that information can be exposed to users without having to know these commands.

===============
Getting Started
===============

In its most basic form, you'll connect to a Varnish_ server through SSH with a username and password

:: 

   simverest.exe <ip address of server> <username> <password>

or

::

   python daemon.py <ip address of server> <username> <password>

This will start collecting information from the Varnish_ server and also start a web server on port 8080 (can be changed via command line switch). Users can then navigate to http://<ip address of simverest>:8080 and they will get a dashboard showing various stats about the Varnish_ server.
   
To get a full list of options, you can use the following command

:: 

   simverest.exe -h

or 

::

   python daemon.py -h


============
API
============

Part of the usefulness of Simverest is that it provides a web api that returns current information about the state of a Varnish_ server.

An example would be the following:

::

   http://localhost:8080/api/servers

returns

::

   {"servers": ["VARNISH1"]}

You can then drill down further to get a full picture of the server:

:: 

   http://localhost:8080/api/server/VARNISH1

returns

::

   {
      "process": {
         "virtualmem":"466m",
         "reservedmem":"111m",
         "cpu":"0.0",
         "memory":"2.8"
      },
      "timestamp":"2012-03-07T22:49:08Z",
      "varnishstats":[
         {
            "name":"client_conn",
            "value":10.428571428571429,
            "description":"Client connections accepted"
         },
         {
            "name":"client_req",
            "value":14.0,
            "description":"Client requests received"
         },
         <snip>...
      ],
      "backends":[
         {
            "timestamp":"2012-03-07T22:48:21Z",
            "state":"healthy",
            "name":"WEB1"
            "status_code": "200",
            "status_text":"OK"
         },
         {
            "timestamp":"2012-03-07T22:48:25Z",
            "state":"sick",
            "name":"WEB2",
            "status_code": "500",
            "status_text":"Internal Server Error"
         }
      ]
   }

Depending on the information required, you can drill down even further

:: 

   http://localhost:8080/api/server/VARNISH1/backend/WEB1/state

returns

::

   healthy


============
Contributing
============

Please submit any bugs to the Github issue tracker: https://github.com/rjnienaber/simverest/issues

If you want to contribute send me a pull request :)

=======
License
=======
Copyright 2012 Richard Nienaber

Simverest is released under the GPL_ license:

If you submit a pull request, please note that you agree that your code will fall under this license.

.. _Varnish: https://www.varnish-cache.org/
__ Varnish_
.. _GPL: http://www.opensource.org/licenses/gpl-3.0.html