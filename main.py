from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float, desc
from flask_wtf import FlaskForm
from wtforms import FloatField, SubmitField, TextAreaField, StringField, IntegerField
from wtforms.validators import DataRequired
from film_api_data import Film_data
import requests





app = Flask(__name__)


app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

db.init_app(app)

class Film(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(unique=True, nullable=False)
    year: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(unique=True, nullable=False) 
    rating: Mapped[float] = mapped_column(nullable=False) 
    ranking: Mapped[int] = mapped_column(nullable=True)
    review:  Mapped[str] = mapped_column(nullable=True)
    img_url:  Mapped[int] = mapped_column(nullable=False)


with app.app_context():
    db.create_all()





class Rating(FlaskForm):
    rating = FloatField('Rating', validators=[DataRequired()])
    review = TextAreaField('Your Review', validators=[DataRequired()])
    done = SubmitField("Done")

class Find_form(FlaskForm):
    title = StringField("Movie Title",   validators=[DataRequired()])
    submit = SubmitField("Find Movie")  



film_data = Film_data()
films = []
MOVIE_DB_IMAGE_URL = "https://image.tmdb.org/t/p/w500"




@app.route("/")
def home():
    rank = 1
    all_film = db.session.execute(db.select(Film).order_by(desc(Film.rating))).scalars().all()
    for x in all_film:
        x.ranking = rank
        rank+=1
    return render_template("index.html", films = all_film)

#update selected film
@app.route("/edit", methods=["GET", "POST"])
def update():
    rating_form = Rating()
    form = rating_form
    film_id = request.args.get('id')
    selected_film = db.get_or_404(Film, film_id )
    if rating_form.validate_on_submit():
       new_rating = rating_form.rating.data
       new_review = rating_form.review.data
       selected_film.rating = new_rating
       selected_film.review = new_review
       db.session.commit()
       return redirect(url_for('home'))
    return render_template("edit.html", selected_film=selected_film, form=form)

#delete selected film
@app.route("/delete")
def delete():
    #getting id of film 
    film_id = request.args.get('id')
    #getting film form db via id
    selected_film = db.get_or_404(Film, film_id )
    #deleting form database
    db.session.delete(selected_film)
    db.session.commit()
    return redirect(url_for('home'))

@app.route("/select")
def select():
     film_id = request.args.get("id")
     #find film details with its id
     if  film_id :
        film_details = film_data.find_with_id(film_id)
     #configure new_movie
        new_movie = Film(
                title=film_details['original_title'],
                year=film_details['release_date'],
                description=film_details['overview'],
                rating=film_details['vote_average'],
                ranking=0,  # Provide a default ranking value or any value that makes sense
                review="",  # Provide a default review value or an empty string
                img_url=f"{MOVIE_DB_IMAGE_URL}{film_details['poster_path']}",
        )
        db.session.add(new_movie)
        db.session.commit()
        #building url for update and id becomes id form new searched film
        return redirect(url_for('update', id=new_movie.id))

     return render_template('select.html', films=films  )

@app.route("/add", methods=["GET", "POST"])
def add_movie():
    global films
    form = Find_form()
    if form.validate_on_submit():
        title = form.title.data
        films = film_data.find_film(title=title)
        
        return redirect( url_for('select'))

    return render_template("add.html", form=form)




if __name__ == '__main__':
    app.run(debug=True)
