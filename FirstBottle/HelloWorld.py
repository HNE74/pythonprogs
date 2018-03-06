'''
Created on 06.03.2018

@author: hnema
'''
from bottle import route, run, static_file

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

run(host='localhost', port=8080, debug=True)
