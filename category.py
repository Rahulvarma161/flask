import os
from flask import render_template
from flask import Flask, flash, request, redirect, url_for
import json,_json
import subprocess
import datetime
import xlrd
from werkzeug.utils import secure_filename
import MySQLdb

ALLOWED_EXTENSIONS = set(['xlsx', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'csv'])


project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = "sqlite:///{}".format(os.path.join(project_dir, "bookdatabase.db"))

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = database_file
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


@app.route("/", methods=["GET", "POST"])
def home():
    db = MySQLdb.connect("localhost", "root", "", "flask_demo")
    cursor = db.cursor()
    books = None
    if request.form:
        try:
            print(request.form)
            data = request.form
            cat_id = data['categories']
            sub_id = data['subcategory']
            db = MySQLdb.connect("localhost", "root", "", "flask_demo")
            cursor = db.cursor()
            sql = "INSERT INTO save_cat_data (cat_id, sub_id) VALUES (%s, %s)"
            val = (cat_id, sub_id)
            cursor.execute(sql, val)
            db.commit()
            return redirect("http://127.0.0.1:5000/", code=302)

        except Exception as e:
            print(e)
    sql = "SELECT * FROM category WHERE is_active=1"
    cursor.execute(sql)
    data = cursor.fetchall()
    print(data)
    data_all = []
    for users in data:
        data_all.append(users)
    print(data_all)
    return render_template("category.html", books=data_all)

@app.route("/subcategoryajax/", methods=["GET", "POST"])
def subcategory():
    try:
        db = MySQLdb.connect("localhost", "root", "", "flask_demo")
        cursor = db.cursor()
        data = request.form
        print(data)
        sql = "SELECT * FROM subcategory WHERE cat_id="+data['categories_id']
        cursor.execute(sql)
        data = cursor.fetchall()
        cursor.close()
        print('here')
        data = list(data)
        print(type(data))
        data=json.dumps(data)
        return data
    except Exception as e:
        print("Failed to add book")
        print(e)
        #return json(data)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def CreateNewDir():
    print ("I am being called")
    global UPLOAD_FOLDER
    UPLOAD_FOLDER = UPLOAD_FOLDER+datetime.datetime.now().strftime("%d%m%y%H")
    cmd="mkdir -p %s && ls -lrt %s"%(UPLOAD_FOLDER,UPLOAD_FOLDER)
    output = subprocess.Popen([cmd], shell=True,  stdout = subprocess.PIPE).communicate()[0]
    if "total 0" in output:
        print ("Success: Created Directory %s"%(UPLOAD_FOLDER))
    else:
        print ("Failure: Failed to Create a Directory (or) Directory already Exists",UPLOAD_FOLDER)


@app.route("/excel/", methods=["GET", "POST"])
def excel():
    books = None
    if request.method == 'POST':
        try:
            file = request.files['excel_file']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                UPLOAD_FOLDER = 'C:/Users/brahul/Downloads/example.flask.crud-app-master/example.flask.crud-app-master/upload_dir/'
                print(UPLOAD_FOLDER)
                #CreateNewDir()
                #global UPLOAD_FOLDER
                file.save(os.path.join(UPLOAD_FOLDER, filename))
            book = xlrd.open_workbook("sample_data.xlsx")
            sheet_names = book.sheet_names()

            for r in range(2):
                if sheet_names[r] == 'category':
                    print('category')
                    sheet = book.sheet_by_name("category")
                    db = MySQLdb.connect("localhost", "root", "", "flask_demo")
                    cursor = db.cursor()
                    query = """INSERT INTO category (categories) VALUES (%s)"""
                    for r in range(1, sheet.nrows):
                            categories	= sheet.cell(r,1).value
                            values = (categories)
                            cursor.execute(query, [values])
                    cursor.close()
                    db.commit()

                else:
                    print('subcat')
                    sheet = book.sheet_by_name("subcategory")
                    db = MySQLdb.connect("localhost", "root", "", "flask_demo")
                    cursor = db.cursor()
                    query = """INSERT INTO subcategory (cat_id,subcategory) VALUES (%s,%s)"""
                    for r in range(1, sheet.nrows):
                        cat_id = int(sheet.cell(r, 0).value)
                        print(cat_id)
                        subcategory = sheet.cell(r, 1).value
                        print(subcategory)
                        values = (int(cat_id),str(subcategory))
                        cursor.execute(query, values)
                    cursor.close()
                    db.commit()
                db.close()
                print('success')
        except Exception as e:
            print(e)
    print(555)
    return render_template("excel.html")


    # Print results

    # columns = str(sheet.ncols)
    # rows = str(sheet.nrows)


if __name__ == "__main__":
    #db.create_all()
    app.run()

