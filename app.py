from flask import Flask, render_template, request
import os, sqlite3
app = Flask(__name__)
path = os.getcwd()+"/static/images"
wsgi_app = app.wsgi_app

class Database():
    def __init__(self, conn, c):
        self.conn = conn
        self.c = c

    def export_filename_database(self):
        with self.conn:
            for filename in os.listdir(path):
                self.c.execute("SELECT filename FROM movies WHERE filename=?",(filename,))
                if self.c.fetchone():
                    pass
                else:
                    self.c.execute("INSERT INTO movies (filename) VALUES (?)", (filename,))

    def import_filename(self):
        with self.conn:
            self.c.execute("SELECT filename FROM movies")
            return self.c.fetchall()

    def export_rating(self, filename, rating):
        with self.conn:
                self.c.execute("UPDATE movies SET rating=? WHERE filename='?'",(rating, filename))

    def import_rating(self):
        with self.conn:
            self.c.execute("SELECT")
                
    def import_all(self):
        class Movie:
            def __init__(self, filename, rating, review):
                self.filename = filename
                self.rating = rating
                self.review = review

        with self.conn:
            self.c.execute("SELECT * FROM movies")
            temp_list = []
            for temp in self.c.fetchall():
                temp_list.append(Movie(temp[0], temp[1], temp[2]))
            return temp_list

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
    database = Database(sqlite3.connect(os.getcwd() +'/static/movie_database.db'), sqlite3.connect(os.getcwd() +'/static/movie_database.db').cursor())
    database.export_filename_database()
    return render_template('index.html', movies = database.import_all())

@app.route('/rate', methods = ["POST","GET"])
def rateMain():
    database = Database(sqlite3.connect(os.getcwd() +'/static/movie_database.db'), 
        sqlite3.connect(os.getcwd() +'/static/movie_database.db').cursor())
    print (database.import_all())
    rating = "No Value"
    if request.method == "POST":
        form = request.form
        filename = request.args.get("imageName")
        for movie in database.import_all():
            if movie.filename == filename:
                database.export_rating(filename, int(form["rating"]))
                rating = "Yes"
    return render_template("rate.html", rating = rating)
    
if __name__ == '__main__':
    import os
    HOST = os.environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(os.environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    app.run(HOST, PORT)
