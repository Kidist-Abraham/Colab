import os
from models import db, connect_db, Stack
from app import app
connect_db(app)


PATH = os.environ.get(
    'LANGUAGE_FILE_PATH', '/Users/kidistabraham/Springboard/Colab/scripts/languages.txt')

def get_words(path):
        f = open(path,"r")
        words = f.read()
        f.close()
        return words.splitlines()


def add_to_db():
    words = get_words("/Users/kidistabraham/Springboard/Colab/scripts/languages.txt")
    words_db = [Stack(name=word) for word in words]
    db.session.add_all(words_db)
    db.session.commit()
    
# uncomment the following to run the function
add_to_db()
