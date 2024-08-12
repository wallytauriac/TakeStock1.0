from flask import Flask, render_template, request, flash
from flask_wtf import Form
from wtforms import StringField, IntegerField, TextAreaField, SubmitField, RadioField, SelectField
from wtforms import validators, ValidationError

app = Flask(__name__)
app.secret_key = 'development key'



class ContactForm(Form):
    name = StringField("Candidate Name ", [validators.data_required("Please enter your name.")])


    Gender = RadioField('Gender', choices=[('M', 'Male'), ('F', 'Female')])
    address = TextAreaField("Address")

    email = StringField("Email", [validators.data_required("Please enter your email address."),
                              validators.Email("Please enter your email address.")])

    Age = IntegerField("Age")
    language = SelectField('Programming Languages', choices=[('java', 'Java'), ('py' 'Python')])

    submit = SubmitField("Submit")

@app.route('/contact', methods=['GET', 'POST'])
def contact():

    form = ContactForm()
    if form.validate() == False:
        flash('All fields are required.')
        return render_template('contact.html')
    return render_template('contact.html', form=form)


@app.route('/success', methods=['GET', 'POST'])
def success():
    return render_template("success.html")


if __name__ == '__main__':
    app.run(debug=True)