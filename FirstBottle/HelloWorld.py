'''
Sample for generating a plot html plage using the Python Bottle Framework
and the Flot Java Script library.
Created on 06.03.2018
@author: Heiko Nolte

'''
from bottle import route, run, static_file
import math

t=0

@route('/hello')
def hello():
    return "Hello World Bottle!"

@route('/<filename:re:.*\.js>')
def javascripts(filename):
    return static_file(filename, root='resources/flot')

@route('/plot')
def plot():
    return '''

<html>
    <head>
        <meta http-equiv="Content-Type" content="text/html"; charset=utf-8>
        <title>FlotPlot</title>
        <style>
            .demo-placeholder {
                width: 80%;
                height: 80%;
            }
        </style>
        
        <script language="javascript" type="text/javascript" src="jquery.js"></script>
        <script language="javascript" type="text/javascript" src="jquery.flot.js"></script>
        
        <script language="javascript" type="text/javascript">
            $(document).ready(function() {
                var data = [];
                for(var i=0; i<500; i++) {
                    data.push([i, Math.exp(-i/100) * Math.sin(Math.PI*i/10)]);
                }

                var plot = $.plot("#placeholder", [data]);
            });
        </script>
    </head>
    
    <body>
        <h3>Flot Plot</h3>
        <div class="demo-container">
            <div id="placeholder" class="demo-placeholder"></div>
        </div>
    </body>
</html>
    '''
    
@route('/plot2')
def plot2():
   return '''
<html>
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    <title>Sinus Curve</title>
    <style>
     .demo-placeholder {
    width: 90%;
    height: 50%;
    }
    </style>
    <script language="javascript" type="text/javascript" 
       src="jquery.js"></script>
    <script language="javascript" type="text/javascript" 
       src="jquery.flot.js"></script>
    <script language="javascript" type="text/javascript" 
       src="jquery.flot.time.js"></script>
    <script language="javascript" type="text/javascript">

$(document).ready(function() {

    // plot options
    var options = {
        series: {
          lines: {
            show: true
          },
          points: {
            show: false
          }
        },
        grid: {
          clickable: false
        },
        yaxes: [{min: -5, max: 5}],
        xaxes: [{min: 0, max: 100}],
    };
    
    // create empty plot
    var plot = $.plot("#placeholder", [[]], options);

    // initialize data arrays
    var Y = [];
    var timeStamp = [];    
    // get data from server
    function getData() {
        // AJAX callback
        function onDataReceived(jsonData) {    
            timeStamp.push(Date());
            // add Y data
            Y.push(jsonData.Y);
            // removed oldest
            if (Y.length > 100) {
              Y.splice(0, 1);
            }

            s1 = [];
            for (var i = 0; i < Y.length; i++) {
                s1.push([i, Y[i]]);
            }
            // set to plot
            plot.setData([s1]);
            plot.draw();
        }

        // AJAX error handler
        function onError(){
            $('#ajax-panel').html('<p><strong>Ajax error!</strong> </p>');
        }
        
        // make the AJAX call
        $.ajax({
            url: "getdata",
            type: "GET",
            dataType: "json",
            success: onDataReceived,
            error: onError
        });        
     }

     // define an update function
     function update() {
        // get data
        getData();
        // set timeout
        setTimeout(update, 200);
     }

     // call update
     update();
});

</script>
</head>

<body>
    <div id="header">
        <h2>Mixed Sinus</h2>
    </div>

    <div id="content">
        <div class="demo-container">
            <div id="placeholder" class="demo-placeholder"></div>
        </div>
        <div id="ajax-panel"> </div>
    </div>    
</body>
</html>
'''
    
@route('/getdata', method='GET')
def getdata():
    global t
    if t is None:
        t = 0
    else:
        t = t + 0.1
    
    y = 3 * math.sin(t) + 2 * math.cos(t+0.5)
    return {"Y": y }

run(host='localhost', port=8080, debug=True)
