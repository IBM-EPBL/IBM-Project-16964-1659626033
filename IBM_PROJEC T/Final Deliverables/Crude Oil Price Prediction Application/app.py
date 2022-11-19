import numpy as np
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
from flask import Flask,render_template,request,redirect,session,url_for,flash
from tensorflow.keras.models import load_model
# import ibm_db
# from .connect import get_db_connection
import ibm_db
def get_db_connection():
    try:
        conn = ibm_db.connect("DATABASE=BLUDB;\
        HOSTNAME=ba99a9e6-d59e-4883-8fc0-d6a8c9f7a08f.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud;\
        PORT=31321;\
        Security=SSL;\
        SSLServerCertificate=DigiCertGlobalRootCA.crt;\
        UID=wvm68663;\
        PWD=o8ZTWcmctkTiXpeR;","","")
        print("Connected to DB")
        return conn
    except:
        print("error r while connecting ",ibm_db.conn_errormsg())
        return 0
con=get_db_connection()
app=Flask(__name__)
app.secret_key="123"
model=load_model('crude_oil.h5',)

name1=input();


@app.route('/')
def home():
    return render_template("index.html")

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/predict')
def home2():
    return render_template("web.html")

@app.route('/back',methods=['GET','POST'])
def back():
    return render_template("web.html")

@app.route('/admin',methods=['GET','POST'])
def admin():
    # if request.method=='POST':
    email=session["email"]
    password=session['password']
        # qry="select * from  USER where email=? AND password=?"
        # stmt=ibm_db.prepare(con,qry)
        # ibm_db.bind_param(stmt,1,email)
        # ibm_db.bind_param(stmt,2,password)
        # ibm_db.execute(stmt)
        # resp=ibm_db.fetch_assoc(stmt)
        # print("resp - ",resp)
    print(email)
    print(password)
    if (email==("admin@gmail.com")):
        if(password==("admin")):
            qry="select NAME from  USER"
            stmt=ibm_db.prepare(con,qry)
            resp=ibm_db.execute(stmt)
            var=ibm_db.fetch_assoc(stmt)
            list1=[]
            while var!=False:
                var=ibm_db.fetch_assoc(stmt)
                list1.append(var)
                var=ibm_db.fetch_assoc(stmt)
            print("resp - ",resp)
            print(list1)
            list1.remove(False)
            print(list1)
            return render_template("admin.html",admin=list1)
    return render_template("web.html")


@app.route('/history')
def history():
    name=session["name"]
    qry="select PRICE from  HISTORY where NAME=?"
    stmt=ibm_db.prepare(con,qry)
    ibm_db.bind_param(stmt,1,name)
    resp3=ibm_db.execute(stmt)
    var=ibm_db.fetch_assoc(stmt)
    price1=[]
    while var!=False:
        var=ibm_db.fetch_assoc(stmt)
        price1.append(var['PRICE'])
        var=ibm_db.fetch_assoc(stmt)
    # prices.remove(False)
    print(resp3)
    print(price1)
    res1 = [eval(i) for i in price1]
    return render_template("history.html",history=res1)

@app.route('/graph')
def graph():
    name=session["name"]
    session["name"]=name
    qry="select PRICE from  HISTORY where NAME=?"
    stmt=ibm_db.prepare(con,qry)
    ibm_db.bind_param(stmt,1,name)
    resp3=ibm_db.execute(stmt)
    var=ibm_db.fetch_assoc(stmt)
    price=[]
    while var!=False:
        var=ibm_db.fetch_assoc(stmt)
        price.append(var['PRICE'])
        var=ibm_db.fetch_assoc(stmt)
    # prices.remove(False)
    print(resp3)
    print(price)
    res = [eval(i) for i in price]
    res2=len(res)
    return render_template("graph.html",history=res,history1=res2)

@app.route('/register',methods=['GET','POST'])
def register():
    if request.method=='POST':
        try:
            name=request.form['name'] 
            email=request.form['email']
            password=request.form['password']
            qry="insert into USER(name,email,password)values(?,?,?)"
            stmt=ibm_db.prepare(con,qry)
            ibm_db.bind_param(stmt,1,name)
            ibm_db.bind_param(stmt,2,email)
            ibm_db.bind_param(stmt,3,password)
            resp2=ibm_db.execute(stmt)
            print(resp2)
            flash("Record Added Successfully","success")
            return render_template("login.html")
        except:
            flash("Error in Insert Operations","danger")
        # finally:
            # return render_template("index.html")
            # con.close()
    return render_template("register.html")


@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        email=request.form['email']
        password=request.form['password']
        qry="select * from  USER where email=? AND password=?"
        stmt=ibm_db.prepare(con,qry)
        ibm_db.bind_param(stmt,1,email)
        ibm_db.bind_param(stmt,2,password)
        ibm_db.execute(stmt)
        resp=ibm_db.fetch_assoc(stmt)
        print("resp - ",resp)
        if resp:
            session["name"]=resp['NAME']
            session["u_id"]=resp['USER_ID']
            session["email"]=resp['EMAIL']
            session["password"]=resp["PASSWORD"]
            return render_template("web.html")
        else:
            flash("Usernaem and Password Mismatch","danger")
            return redirect("login")

    return render_template("login.html")

@app.route('/prediction',methods=['POST'])
def prediction():
    x_input=str(request.form['year'])
    x_input=x_input.split(',')
    print(x_input)
    for i in range(0,len(x_input)):
        x_input[i]=float(x_input[i])
    print(x_input)
    x_input=np.array(x_input).reshape(1,-1)
    temp_input=list(x_input)
    temp_input=temp_input[0].tolist()
    lst_output=[]
    n_steps=10
    i=0
    while(i<1):
        if(len(temp_input)>10):
            x_input=np.array(temp_input[1:])
            print("{} day input {}".format(i,x_input))
            x_input=x_input.reshape(1,-1)
            x_input=x_input.reshape((1,n_steps,1))

            yhat=model.predict(x_input,verbose=0)
            print("{} day output {}".format(i,yhat))
            temp_input.extend(yhat[0].tolist())
            temp_input=temp_input[1:]

            lst_output.extend(yhat.tolist())
            i=i+1

        else:
            x_input=x_input.reshape((1,n_steps,1))
            yhat=model.predict(x_input,verbose=0)
            print(yhat[0])
            temp_input.extend(yhat[0].tolist())
            print(len(temp_input))
            lst_output.extend(yhat.tolist())
            i=i+1

        name=session["name"]
        u_id=session["u_id"]
        qry="insert into HISTORY(USER_ID,NAME,PRICE) values(?,?,?)"
        stmt=ibm_db.prepare(con,qry)
        ibm_db.bind_param(stmt,1,u_id)
        ibm_db.bind_param(stmt,2,name)
        ibm_db.bind_param(stmt,3,str(lst_output[0][0]))
        resp2=ibm_db.execute(stmt)
        print(resp2)
        
        return render_template("web.html",showcase='The next day predicted value is:'+str(lst_output[0][0]))


if __name__=='__main__':
    app.run(debug=True,port=5000)