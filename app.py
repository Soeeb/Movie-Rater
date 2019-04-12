from flask import Flask, render_template, request
import os, sqlite3
app = Flask(__name__)
path = os.getcwd()+"/static/images"
wsgi_app = app.wsgi_app

def add_to_file():
    with conn:
        c = conn.cursor()
        for filename in os.listdir(path):
            c.execute("SELECT filename FROM movies WHERE filename=?",(filename,))
            if c.fetchone():
                pass
            else:
                c.execute("INSERT INTO movies (filename) VALUES (?)", (filename,))

def import_filename():
    with conn:
        c.execute("SELECT filename FROM movies")
        return c.fetchall()

#used during first time to create a table
#c.execute("""CREATE TABLE movies (
#            filename text,
#            rateing inter,
#            review text)
#            """)

class Movie:
    def __init__(self, filename):
        self.filename = filename
        self.rating = []
        self.review = ""

@app.route('/')
def main():
    conn = sqlite3.connect(os.getcwd() +'/static/movie_database.db')
    c = conn.cursor()

    add_to_file()
    movies = []
    movies_import = import_filename()
    for movie in movies_import:
        movies.append(Movie(movie[0]))
    return render_template('index.html', movies = movies)

if __name__ == '__main__':
    import os
    HOST = os.environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(os.environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    app.run(HOST, PORT)
