from flask_sqlalchemy import SQLAlchemy

# creating the db and connecting to it
DB = SQLAlchemy()


class User(DB.Model):
    # id
    id = DB.Column(DB.BigInteger, primary_key=True)
    # username
    username = DB.Column(DB.String, nullable=False)
    # newest tweet id
    newest_tweet_id = DB.Column(DB.BigInteger)

    def __repr__(self):
        return f"<User: {self.username}>"

class Tweet(DB.Model):
    # id
    id = DB.Column(DB.BigInteger, primary_key=True)
    # text
    text = DB.Column(DB.Unicode(300))
    # user_id
    user_id = DB.Column(DB.BigInteger, DB.ForeignKey('user.id'), 
        nullable=False)
    # user
    # Going to add an attribute to both tables (User and Tweet)
    user = DB.relationship('User', backref=DB.backref('tweets', lazy=True))

    # place to store our word embeddings "vectorization"
    vect = DB.Column(DB.PickleType, nullable=False)

    def __repr__(self):
        return f"<Tweet:{self.text}>"