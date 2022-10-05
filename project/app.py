
import os
from bson import ObjectId
from flask import Flask, render_template, request, url_for, redirect, session
from password import getPassword
import pymongo
import bcrypt
from datetime import datetime


url = "/project/templates/"
app = Flask(__name__)


app.secret_key = "testing"
client = pymongo.MongoClient(
    'mongodb+srv://HarenAdmin:' +getPassword()+ '@cluster0.xvhizro.mongodb.net/test')

db = client.get_database('blog_app')
records = db.user



@app.route("/", methods=['POST', 'GET'])
def index():
    message = ''
    if "user" in session:
        return redirect(url_for("logged_in"))
    if request.method == "POST":
        user = request.form.get("user")
        
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        
        user_found = records.find_one({"user": user})
        if user_found:
            message = 'There already is a user by that name'
            return render_template('index.html', message=message)
        if password1 != password2:
            message = 'Passwords should match!'
            return render_template('index.html', message=message)
        else:
            hashed = bcrypt.hashpw(password2.encode('utf-8'), bcrypt.gensalt())
            user_input = {'user': user, 'password': hashed}
            records.insert_one(user_input)
            
            user_data = records.find_one({"user": user})
            new_user = user_data['user']
   
            return render_template('logged_in.html', user=new_user)
    return render_template('index.html')


@app.route('/logged_in')
def logged_in():
    if "user" in session:
        user = session["user"]
        return render_template('logged_in.html', user=user)
    else:
        return redirect(url_for("login"))


@app.route("/login", methods=["POST", "GET"])
def login():
    message = 'Please login to your account'
    if "user" in session:
        return redirect(url_for("logged_in"))

    if request.method == "POST":
        user = request.form.get("user")
        password = request.form.get("password")

       
        user_found = records.find_one({"user": user})
        if user_found:
            user_val = user_found['user']
            passwordcheck = user_found['password']
            
            if bcrypt.checkpw(password.encode('utf-8'), passwordcheck):
                session["user"] = user_val
                return redirect(url_for('logged_in'))
            else:
                if "user" in session:
                    return redirect(url_for("logged_in"))
                message = 'Wrong password'
                return render_template('login.html', message=message)
        else:
            message = 'User not found'
            return render_template('login.html', message=message)
    return render_template('login.html', message=message)



@app.route("/newpost", methods=["POST", "GET"])
def newpost():
    title = request.form.get("title")
    content = request.form.get("content")
    message = 'Please login to your account'
    if "user" not in session:
        message = 'Session Expired! Please login to your account'
        return redirect(url_for("login"))

    if title == "" or content == "":
        return render_template('newpost.html')
    
    if request.method == "POST":

        newpost = db.post
        # datetime object containing current date and time
        now = datetime.now()
        print()
        # dd/mm/YY H:M:S
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        print("date and time =", dt_string)	
        user_input = {'title': title, 'content': content, 'creator': session["user"], 'posted_at': dt_string}
        print(user_input)


        newpost.insert_one(user_input)
        return render_template('mainfeed.html', message=message)


    return render_template('newpost.html', message=message)


@app.route("/updatepost/<post_id>", methods=["POST", "GET"])
def updatePost(post_id):
    title = request.form.get("title")
    content = request.form.get("content")
    
    if not(title or content):
        post = db.post.find_one({"_id":ObjectId(post_id,)})
        return render_template('updatepost.html', post=post)
    else:
        db.post.update_one({"_id":ObjectId(post_id,)}, {"$set" :{"title": title, "content": content}})
        posts = db.post.find({"creator": session["user"]})
        return render_template('userfeed.html', posts=posts, user=session["user"])
        



@app.route("/deletepost/<post_id>")
def deletePost(post_id):
    db.post.delete_one({"_id":ObjectId(post_id,)})
    posts = db.post.find({"creator": session["user"]})
    return render_template('userfeed.html', posts=posts, user=session["user"])



@app.route("/mainfeed", methods=["POST", "GET"])
def mainfeed():
    posts = db.post.find()
    return render_template('mainfeed.html', posts=posts)

@app.route("/userfeed", methods=["POST", "GET"])
def userfeed():

    posts = db.post.find({"creator": session["user"]})
    if "user" not in session:
        return render_template('login.html')

    return render_template('userfeed.html', posts=posts, user=session["user"])



@app.route("/logout", methods=["POST", "GET"])
def logout():
    if "user" in session:
        session.pop("user", None)
        return render_template("signout.html")
    else:
        return render_template('index.html')

#end of code to run it
if __name__ == "__main__":
  app.run(debug=True)