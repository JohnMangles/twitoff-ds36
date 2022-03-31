from flask import Flask, render_template, request
from twitoff.predict import predict_user
from .predict import predict_user
from .models import DB, User, Tweet
from .twitter import add_or_update_user
from sklearn.datasets import load_iris
from sklearn.linear_model import LogisticRegression
from os import getenv

# Flask Factory
def create_app():
    app = Flask(__name__)

    # Tell our app where to find our database
    app.config['SQLALCHEMY_DATABASE_URI'] = getenv("DATABASE_URI")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    DB.init_app(app)

    @app.route("/")
    def home():
        # query database for all users
        users = User.query.all()
        return render_template("base.html", title='Home', users=users)


    @app.route("/reset")
    def reset():
        # Drop our DB tables
        DB.drop_all()
        # Creates our DB tables
        DB.create_all()
        return render_template("base.html", title='Reset DB')
    
    @app.route('/update')
    def update():
        usernames = [user.username for user in User.query.all()]
        for username in usernames:
            add_or_update_user(username)
        return render_template('base.html', title='Update')

    @app.route('/iris')
    def iris():
        X, y = load_iris(return_X_y=True)
        clf = LogisticRegression(random_state=42, solver='lbfgs',
                                multi_class='multinomial').fit(X,y)
        
        return str(clf.predict(X[:2,:]))

    @app.route('/user', methods=["POST"])
    @app.route('/user/<name>', methods=["GET"])
    def user(name=None, message=''):

        # we either take name that was passed in or we pull it
        # from our request.values which would be accessed through the
        # user submission
        name = name or request.values['user_name']
        try:
            if request.method == 'POST':
                add_or_update_user(name)
                message = "User {} Succesfully added!".format(name)

            tweets = User.query.filter(User.username == name).one().tweets

        except Exception as e:
            message = "Error adding {}: {}".format(name, e)

            tweets = []

        return render_template("user.html",
                                title=name,
                                tweets=tweets,
                                message=message)

    @app.route('/compare', methods=['POST'])
    def compare():
        user0 = request.values['user0']
        user1 = request.values['user1']

        if user0 == user1:
            message = "Cannot compare a user to themselves"
        else:
            text = request.values['tweet_text']
            prediction = predict_user(user0, user1, text)
            message= '{} is more likely to be said by {} than {}!'.format(
                text,
                user1 if prediction else user0,
                user0 if prediction else user1
            )
        return render_template('prediction.html',
                                title='Prediction',
                                message=message)


    return app
