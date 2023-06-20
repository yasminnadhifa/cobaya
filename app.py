from flask import Flask,redirect,url_for,render_template,request,make_response
import pdfcrowd
from pymongo import MongoClient
from werkzeug.utils import secure_filename
from datetime import datetime
from bson import ObjectId

import os
from os.path import join,dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__),'.env')
load_dotenv(dotenv_path)


MONGODB_URI = os.environ.get('MONGODB_URI')
DBNAME = os.environ.get('DBNAME')

client = MongoClient(MONGODB_URI)
db = client[DBNAME]

app=Flask(__name__)
@app.route('/',methods=['GET','POST'])
def home():
    data = list(db.pengaduan.find({}))
    for d in data:
        d["_id"] = str(d["_id"])
    pengaduan = db.pengaduan.count_documents({})
    print(data)
    return render_template("index.html",data=data, pengaduan=pengaduan)

@app.route('/edit',methods=['GET','POST'])
def edit():
    if request.method == "GET":
        id = request.args.get("id")
        data = db.pengaduan.find_one({"_id":ObjectId(id)})
        data["_id"] = str(data["_id"])
        print(data)
        return render_template("edit.html",data=data)
    
    id = request.form["id"]
    status = request.form["status"]
    file_path= ""
    file = request.files["pdf"]
    if file:
        filename = secure_filename(file.filename)
        extension = filename.split(".")[-1]
        today = datetime.now()
        mytime = today.strftime('%Y-%m-%d-%H-%M-%S')
        file_path = f'pengaduan-{mytime}.{extension}'
        file.save("./static/coba/" + file_path)
    db.pengaduan.update_one({"_id":ObjectId(id)},{'$set':{"status":status,"surat":file_path}})
    return redirect('/')

@app.route('/convert_to_pdf', methods=['GET','POST'])
def convert_to_pdf():
    data = {
        "nama":request.form['nama'],
        "gender":request.form['gender']
    }
    html = render_template('report.html',data=data)  

    client = pdfcrowd.HtmlToPdfClient('yasminlx', 'd75367f4f7c5a13eeb9eb90055728277')  
    pdf = client.convertString(html)

    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=output.pdf'  
    return response

if __name__ == '__main__':
    app.run(port=5000,debug=True)