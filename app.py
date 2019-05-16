#Importing any libraires need for the code to run as well as declaring any varibles that will be used instead of fill length,
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
import os, sqlite3
app = Flask(__name__)
app.secret_key = 'very_secret'
path = os.getcwd()+"/static/images"
wsgi_app = app.wsgi_app
app.config['UPLOAD_FOLDER'] = path 
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

def export_filename_database(c, conn):
    with conn:
        for filename in os.listdir(path):
            c.execute("SELECT filename FROM movies WHERE filename=?",(filename,))
            if c.fetchone():
                pass
            else:
                c.execute("INSERT INTO movies (filename) VALUES (?)", (filename,))
        conn.commit()

#used to import all info from database into a list that can be easily used by the program as well as future proofing the program
def import_all(c, conn):
    class Movie:
        def __init__(self, filename, rating, review, year, director, studio, title):
            self.filename = filename
            self.rating = rating
            self.review = review
            self.year = year
            self.director = director
            self.studio = studio
            self.title = title

    with conn:
        c.execute("SELECT * FROM movies")
        temp_list = []
        for temp in c.fetchall():
            temp_list.append(Movie(temp[0], temp[1], temp[2], temp[3], temp[4], temp[5], temp[6]))
        return temp_list

#all functions below are used for database management   
def import_filename(c, conn):
    c.execute("SELECT filename FROM movies")
    return c.fetchall()

def export_rating(filename, rating, c, conn):
    with conn:
        c.execute("UPDATE movies SET rating=? WHERE filename=?",(rating, filename))

def import_rating(c, conn, filename):
    with conn:
        c.execute("SELECT rating FROM movies WHERE filename=?", (filename,))
        output = c.fetchone()
        return output[0]
                
def export_review(c, conn, review, filename):
    with conn:
        c.execute("UPDATE movies SET review=? WHERE filename=?",(review, filename))

def import_review(c, conn, filename):
    with conn:
        c.execute("SELECT review FROM movies WHERE filename=?", (filename,))
        output = c.fetchone()
        return output[0]

def import_upload(c, conn, filename):
    with conn:
        c.execute("INSERT INTO movies (filename) VALUES (?)", (filename,))

def delete(c, conn, filename):
    c.execute('DELETE FROM movies WHERE filename=?',(filename,))
    os.remove(path + "/" + filename)

def export_year(c, conn, year, filename):
    with conn:
        c.execute("UPDATE movies SET year=? WHERE filename=?",(year, filename))

def import_year(c, conn, filename):
    with conn:
        c.execute("SELECT year FROM movies WHERE filename=?", (filename,))
        output = c.fetchone()
        return output[0]

def export_director(c, conn, director, filename):
    with conn:
        c.execute("UPDATE movies SET director=? WHERE filename=?",(director, filename))

def import_director(c, conn, filename):
    with conn:
        c.execute("SELECT director FROM movies WHERE filename=?", (filename,))
        output = c.fetchone()
        return output[0]
    
def export_studio(c, conn, studio, filename):
    with conn:
        c.execute("UPDATE movies SET studio=? WHERE filename=?",(studio, filename))

def import_studio(c, conn, filename):
    with conn:
        c.execute("SELECT studio FROM movies WHERE filename=?", (filename,))
        output = c.fetchone()
        return output[0]

def export_title(c, conn, title, filename):
    with conn:
        c.execute("UPDATE movies SET title=? WHERE filename=?",(title, filename))

def import_title(c, conn, filename):
    with conn:
        c.execute("SELECT title FROM movies WHERE filename=?", (filename,))
        output = c.fetchone()
        return output[0]

def close(c, conn):
    conn.commit()
    conn.close()

#used remove the file extension from the file and return it
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#used during first time to create a table
'''
conn = sqlite3.connect(os.getcwd() +'/static/movie_database.db')
c = conn.cursor()
c.execute("""CREATE TABLE movies (
            filename text,
            rating inter,
            review text,
            year inter,
            director text,
            studio text,
            title text)
            """)'''
       
@app.route('/') #app route used for homepage
def main(): 
    conn = sqlite3.connect(os.getcwd() +'/static/movie_database.db') #used to establish connection with database.
    c = conn.cursor()
    export_filename_database(c, conn)
    movies = import_all(c, conn)
    close(c, conn)
    return render_template('index.html', movies = movies)

@app.route('/rate', methods = ["POST","GET"]) #app route used for rating webpage
def rateMain(): 
    conn = sqlite3.connect(os.getcwd() +'/static/movie_database.db') #used to establish connection with database.
    c = conn.cursor()
    #importing everything that is need from the database and declaring them as variables to be used easily
    filename = request.args.get("imageName")
    rating = import_rating(c, conn, filename)
    review = import_review(c, conn, filename)
    year = import_year(c, conn, filename)
    director = import_director(c, conn, filename)
    studio = import_studio(c, conn, filename)
    title = import_title(c, conn, filename)
    if request.method == "POST":
        if request.form.get('submit') == 'submit': #checking whether the submit button has been clicked or if the delete button as been clicked
            form = request.form
            for movie in import_all(c, conn):
                if movie.filename == filename:
                #code below used to export all changes to the database.
                    export_rating(filename, int(form["rating"]), c, conn)
                    export_review(c, conn, form["review"], filename)
                    review = form["review"]
                    export_director(c, conn, form['director'], filename)
                    export_studio(c, conn, form['studio'], filename)
                    export_title(c, conn, form['title'], filename)
                    export_year(c, conn, int(form['year']), filename)
                    flash("Movie reviewed successfully!", "success")
                    return redirect(request.url) 
        elif request.form.get('delete') == 'delete':  #checking whether the submit button has been clicked or if the delete button as been clicked
            delete(c, conn, filename) #running function that deletes both the file from the file directory as well as it's entry in the database
            close(c, conn) #closing databse to commit the delete
            flash("File deleted successfully!", "success") #notify for successfully deleted file
            return redirect(url_for('main'))
    close(c, conn)
    return render_template("rate.html", rating = rating, review = review, year = year, director = director, studio = studio, title = title)

@app.route('/upload', methods = ["POST", "GET"]) #app route used to upload page
def uploadMain():
    conn = sqlite3.connect(os.getcwd() +'/static/movie_database.db') #used to establish connection with database.
    c = conn.cursor()
    if request.method == "POST":
        if 'file' not in request.files: #use to test if a file with an extenstion has been selected
            flash('No file extension!', 'warning')
            return redirect(request.url)
        file = request.files["file"]
        if file.filename == "": #test if file has been selected
            flash('No file selected!', 'warning')
            return redirect(request.url)
            #used to test if file extension is the correct and if all entries are been filled
        if file and allowed_file(file.filename) and request.form['director'] != "" and request.form['studio'] != "" and request.form['title'] != "" and request.form['year'] != "":
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                import_upload(c, conn, filename)
                export_director(c, conn, request.form['director'], filename)
                export_studio(c, conn, request.form['studio'], filename)
                export_title(c, conn, request.form['title'], filename)
                export_year(c, conn, int(request.form['year']), filename)
                flash("File has been uploaded successfully!", "success")
        else:
        #used to notify user of incorret entries
            flash('Incorrect file type!/Not all forms filled in!', 'warning')
    return render_template("upload.html")
    
if __name__ == '__main__':
    import os
    HOST = os.environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(os.environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    app.run(HOST, PORT)
