from flask import Flask,request, url_for, redirect, render_template
import pickle
import numpy as np

app = Flask(__name__, template_folder='template')

model=pickle.load(open('model.pkl','rb'))


@app.route('/')
def hello_world():
    return render_template("house_price_predictor.html")


@app.route('/predict',methods=['POST','GET'])
def predict():
    print('Request', request.form)
    #for x in request.form.values():
       # print(x)
    
    '''
    int_features=[int(x) for x in request.form.values()]
    final=[np.array(int_features)]
    print(int_features)
    print(final)
    prediction=model.predict(final)
    print(prediction)
    output='{0}'.format(prediction[0])
    print(output)

    return render_template('house_price_predictor.html',pred='Price of housing unit is {}'.format(output))
    '''


if __name__ == '__main__':
    app.run(debug=True)
