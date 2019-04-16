from flask import Flask, render_template, request
import os, sqlite3
app = Flask(__name__)
path = os.getcwd()+"/static/images"
wsgi_app = app.wsgi_app

def add_to_file(conn, c):
    with conn:
        for filename in os.listdir(path):
            c.execute("SELECT filename FROM movies WHERE filename=?",(filename,))
            if c.fetchone():
                pass
            else:
                c.execute("INSERT INTO movies (filename) VALUES (?)", (filename,))

def import_filename(conn, c):
    with conn:
        c.execute("SELECT filename FROM movies")
        return c.fetchall()

def import_file_all(conn,c):
    class Movie:
        def __init__(self, filename, rating, review):
            self.filename = filename
            self.rating = rating
            self.review = review

        def 

    with conn:
        c.execute("SELECT * FROM MOVIES")
        temp_list = []
        for temp in c.fetchall():
            temp_list.append(Movie(temp[0], temp[1], temp[2]))
        return temp_list

#used during first time to create a table
#c.execute("""CREATE TABLE movies (
#            filename text,
#            rateing inter,
#            review text)
#            """)



@app.route('/')
def main():
    conn = sqlite3.connect(os.getcwd() +'/static/movie_database.db')
    c = conn.cursor()
    add_to_file(conn, c)
    movies = import_file_all(conn,c)
    return render_template('index.html', movies = movies)


@app.route('/rate', methods = ["POST","GET"])
def rateMain():
    conn = sqlite3.connect(os.getcwd() +'/static/movie_database.db')
    c = conn.cursor()
    movies = import_file_all(conn,c)
    rating = None
    if request.method == "POST":
        form = request.form
        filename = request.args.get("imageName")
    return render_template("rate.html", rating = rating)
    

if __name__ == '__main__':
    import os
    HOST = os.environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(os.environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    app.run(HOST, PORT)
