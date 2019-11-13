import flask
from flask import request, redirect, render_template
from api import make_prediction
from flask import jsonify
import json
import plotly
import plotly.graph_objects as go
import numpy as np

# Initialize the app
app = flask.Flask(__name__)

# An example of routing:
# If they go to the page "/" (this means a GET request
# to the page http://127.0.0.1:5000/), return a simple
# page that says the site is up!

with open('database.json') as dataku:
    data = json.load(dataku)

user = []

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        nam_l = request.form['nama_login']
        pwd_l = request.form['pass_login']
        if str(data) == '[]':
            return render_template('loginerror.html', nama = nam_l)
        else:
            for a in range(len(data)):
                if nam_l == data[a]['nama'] and pwd_l == data[a]['pass']:
                    user.append(str(nam_l))
                    return redirect('/')
                elif a == len(data) - 1:
                    return render_template('loginerror.html')
                else:
                    continue
    else:
        if str(user) != '[]':
            return redirect('/')
        else:
            return render_template('login.html')

@app.route('/signup', methods = ['GET', 'POST'])
def signup():
    if request.method == 'POST':
        nam_s = request.form['nama_signup']
        pwd_s = request.form['pass_signup']
        lis = []
        for i in range(len(data)):
            lis.append(data[i]['nama'])
        if str(nam_s) not in lis:
            data.append({'nama': nam_s, 'pass': pwd_s})
            y = json.dumps(data)

            json_data = open('database.json', 'w')
            json_data.write(y)
            return redirect('/')
        else:
            return render_template('signupexists.html')
    else:
        if str(user) != '[]':
            return redirect('/main')
        else:
            return render_template('signup.html')


@app.route("/", methods=["POST"])
def print_piped():
    if request.form['mes']:
        msg = request.form['mes']
        print(msg)
        x_input, predictions = make_prediction(str(msg))
        flask.render_template('predictor.html',
                                user=user[0],
                                chat_in=x_input,
                                prediction=predictions)
    return jsonify(predictions)

@app.route("/", methods=["GET"])
def predict():
    if str(user)=='[]':
        return redirect('/login')
    else:
    # request.args contains all the arguments passed by our form
    # comes built in with flask. It is a dictionary of the form
    # "form name (as set in template)" (key): "string in the textbox" (value)
        print(request.args)
        if(request.args):
            x_input, predictions = make_prediction(request.args['chat_in'])
            print(x_input)
            x = [item['name'] for item in predictions]
            y = [round(item['prob'] *100, 2) for item in predictions]
            yx = [str(item)+'%' for item in y]
            plot = go.Bar(x=x, y=y,text=yx, marker={'color': y,'colorscale': 'tealgrn'},
            textposition='auto',width=[0.6, 0.6, 0.6, 0.6, 0.6, 0.6])
            plotJSON = json.dumps([plot],cls = plotly.utils.PlotlyJSONEncoder)
            return flask.render_template('predictor.html',
                                        user=user[0],
                                        chat_in=x_input,
                                        prediction=predictions,
                                        x = plotJSON)
        else: 
            #For first load, request.args will be an empty ImmutableDict type. If this is the case,
            # we need to pass an empty string into make_prediction function so no errors are thrown.
            x_input, predictions = make_prediction('')
            x = [item['name'] for item in predictions]
            y = [0 for item in predictions]
            yx = [0 for item in y]
            plot = go.Bar(x=x, y=y,text=yx, marker={'color': y,'colorscale': 'tealgrn'},
            textposition='auto',width=[0.6, 0.6, 0.6, 0.6, 0.6, 0.6])
            plotJSON = json.dumps([plot],cls = plotly.utils.PlotlyJSONEncoder)
            return flask.render_template('predictor.html',
                                        user=user[0],
                                        chat_in=x_input,
                                        prediction=predictions,
                                        x = plotJSON)
        print(predictions)

@app.route('/logout', methods = ['GET', 'POST'])
def logout():
    user.clear()
    return redirect('/login')

# @app.route('/guide', methods = ['GET'])
# def guide():
#     return render_template('guide.html',user=user[0])

# @app.route('/about', methods = ['GET'])
# def about():
#     return render_template('about.html',user=user[0])
                                     
# Start the server, continuously listen to requests.

if __name__=="__main__":
    app.run(debug=True)
    app.run()
