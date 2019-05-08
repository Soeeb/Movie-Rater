from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import os, sqlite3
app = Flask(__name__)
path = os.getcwd()+"/static/images"
wsgi_app = app.wsgi_app
app.config['UPLOAD_FOLDER'] = path 

def export_filename_database(c, conn):
    with conn:
        for filename in os.listdir(path):
            c.execute("SELECT filename FROM movies WHERE filename=?",(filename,))
            if c.fetchone():
                pass
            else:
                c.execute("INSERT INTO movies (filename) VALUES (?)", (filename,))
        conn.commit()

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

def import_all(c, conn):
    class Movie:
        def __init__(self, filename, rating, review):
            self.filename = filename
            self.rating = rating
            self.review = review

    with conn:
        c.execute("SELECT * FROM movies")
        temp_list = []
        for temp in c.fetchall():
            temp_list.append(Movie(temp[0], temp[1], temp[2]))
        return temp_list

def close(c, conn):
    conn.commit()
    conn.close()

#used during first time to create a table
'''
conn = sqlite3.connect(os.getcwd() +'/static/movie_database.db')
c = conn.cursor()
c.execute("""CREATE TABLE movies (
            filename text,
            rating inter,
            review text)
            """)  '''
       
@app.route('/')
def main():
    conn = sqlite3.connect(os.getcwd() +'/static/movie_database.db')
    c = conn.cursor()
    export_filename_database(c, conn)
    movies = import_all(c, conn)
    close(c, conn)
    return render_template('index.html', movies = movies)

@app.route('/rate', methods = ["POST","GET"])
def rateMain():
    conn = sqlite3.connect(os.getcwd() +'/static/movie_database.db')
    c = conn.cursor()
    filename = request.args.get("imageName")
    rating = import_rating(c, conn, filename)
    review = import_review(c, conn, filename)
    if request.method == "POST":
        if request.form.get('submit') == 'submit':
            form = request.form
            for movie in import_all(c, conn):
                if movie.filename == filename:
                    export_rating(filename, int(form["rating"]), c, conn)
                    rating = int(form["rating"])
                    export_review(c, conn, form["review"], filename)
                    review = form["review"]
        elif request.form.get('delete') == 'delete':
            delete(c, conn, filename)
            close(c, conn)
            return redirect(url_for('main'))
    close(c, conn)
    return render_template("rate.html", rating = rating, review = review)

@app.route('/upload', methods = ["POST", "GET"])
def uploadMain():
    conn = sqlite3.connect(os.getcwd() +'/static/movie_database.db')
    c = conn.cursor()
    uploaded = "No file uploaded"
    if request.method == "POST":
       file = request.files["file"]
       filename = secure_filename(file.filename)
       file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
       import_upload(c, conn, filename)
       uploaded = "File uploaded succesfully!"
    return render_template("upload.html", uploaded = uploaded)
    
if __name__ == '__main__':
    import os
    HOST = os.environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(os.environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    app.run(HOST, PORT)
