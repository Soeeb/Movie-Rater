from flask import Flask, render_template, request
import os, sqlite3
app = Flask(__name__)
path = os.getcwd()+"/static/images"
wsgi_app = app.wsgi_app

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
        return c.fetchone()
                
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
    print (import_all(c, conn))
    filename = request.args.get("imageName")
    rating = import_rating(c, conn, filename)
    if request.method == "POST":
        form = request.form
        for movie in import_all(c, conn):
            if movie.filename == filename:
                export_rating(filename, int(form["rating"]), c, conn)
                rating = int(form["rating"])
    close(c, conn)
    return render_template("rate.html", rating = rating)
    
if __name__ == '__main__':
    import os
    HOST = os.environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(os.environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    app.run(HOST, PORT)
