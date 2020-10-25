import time

from flask import Flask, render_template, request, redirect, session, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SECRET_KEY'] = 'the random string'
db = SQLAlchemy(app)


#################### All the databases ################################
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    password = db.Column(db.String(50))
    typeOfAccount = db.Column(db.String(10))
    credentials = db.Column(db.String(50))
    image = db.Column(db.String(50))
    about = db.Column(db.String(50))
    skills = db.Column(db.String(50))
    institute = db.Column(db.String(50))
    verifiedskills = db.Column(db.String(50))
    github = db.Column(db.String(50))
    linkedin = db.Column(db.String(50))
    score = db.Column(db.Integer, default=100)


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(50))
    shortdescription = db.Column(db.String(200))
    detaileddescription = db.Column(db.String(200))
    pay = db.Column(db.Integer)
    tags=db.Column(db.String(50))
    status = db.Column(db.Integer, default='Pending')
    askedby_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    askedby_name = db.Column(db.String(200))
    askedby_img = db.Column(db.String(200))


class Response(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    image = db.Column(db.String(50))
    description = db.Column(db.String(200))
    pay = db.Column(db.Integer)
    questionID = db.Column(db.Integer, db.ForeignKey('question.id'))


class Assigned(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    createdbyId = db.Column(db.Integer, db.ForeignKey('user.id'))
    questionID = db.Column(db.Integer, db.ForeignKey('question.id'))
    assignedto_ID = db.Column(db.Integer, db.ForeignKey('user.id'))
    # To display the name of user and question in history section
    questionName = db.Column(db.String(200))
    assignedName = db.Column(db.String(200))


class Recruiter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200))
    password = db.Column(db.String(50))
    company = db.Column(db.String(200))
    credentials = db.Column(db.String(50))
    image = db.Column(db.String(50))
    roles = db.Column(db.String(50))


class Interview(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(50), default='Pending')
    date = db.Column(db.Integer)
    time = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    recruiter_id = db.Column(db.Integer, db.ForeignKey('recruiter.id'))
    # To display the name of user and question in history section
    username = db.Column(db.String(50))
    userabout = db.Column(db.String(50))
    recruitername = db.Column(db.String(50))


################################  REGISTER  LOGIN  LOGOUT ROUTES ###################################

@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        username = request.form['username']
        password = request.form['password']
        data = User.query.filter_by(username=username,
                                    password=password).first()

        if data is not None:
            session['user'] = data.id
            print(session['user'])
            return redirect(url_for('index'))

        return render_template('incorrectLogin.html')


@app.route('/register/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        new_user = User(username=request.form['username'],
                        password=request.form['password'], typeOfAccount=request.form['typeOfAccount'],
                        credentials=request.form['credentials'], institute=request.form['institute'],
                        skills=request.form['skills'], image=request.form['image'], about=request.form['about'],
                        github=request.form['github'], linkedin=request.form['linkedin'])

        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))


###########Recruiter##################

@app.route('/Rlogin', methods=['GET', 'POST'])
def Rlogin():
    if request.method == 'GET':
        return render_template('Rlogin.html')
    else:
        username = request.form['username']
        password = request.form['password']
        data = Recruiter.query.filter_by(username=username,
                                         password=password).first()
        if data is not None:
            session['user'] = data.id
            print(session['user'])
            return redirect(url_for('Rindex'))

        return render_template('incorrectLogin.html')


@app.route('/Rregister/', methods=['GET', 'POST'])
def Rregister():
    if request.method == 'POST':
        new_recruiter = Recruiter(username=request.form['username'],
                                  password=request.form['password'], company=request.form['company'],
                                  credentials=request.form['credentials'], image=request.form['image'],
                                  roles=request.form['roles'])

        db.session.add(new_recruiter)
        db.session.commit()
        return redirect(url_for('Rlogin'))
    return render_template('Rregister.html')


@app.route('/Rlogout', methods=['GET', 'POST'])
def Rlogout():
    session.pop('username', None)
    print("session closed")
    return redirect(url_for('login'))


######################################### CRUD Model ####################################

@app.route('/index')
def index():
    user_id = session['user']
    username = User.query.get(session['user']).username
    print('*' * 30)
    print('YOU ARE LOGGINED IN AS', username)  # All those print statments are for testing purpose. Ignore them
    print('*' * 30)
    flash("welcome {}".format(username))
    today = time.strftime("%m/%d/%Y")
    showQuestion = Question.query.order_by(desc(Question.id))
    rank_user = User.query.order_by(desc(User.score))
    interview = Interview.query.filter_by(user_id=user_id).filter_by(status='Confirmed').order_by(Interview.date).all()
    return render_template('index.html', showQuestion=showQuestion, rank_user=rank_user, interview=interview,
                           today=today)


# Route to add a new question
@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        user_id = session['user']
        getTagsArrays=request.form.getlist('tags')
        t=''
        for eachTag in getTagsArrays:
            t += "      "
            t += eachTag
            t += "   |   "
        print('getTagsArrays',getTagsArrays, 'eachTag',t)
        print(user_id)
        new_question = Question(question=request.form['question'],
                                shortdescription=request.form['shortdescription'],
                                detaileddescription=request.form['detaileddescription'],
                                pay=request.form['pay'], tags=t, askedby_id=user_id,
                                askedby_name=User.query.get(user_id).username,
                                askedby_img=User.query.get(user_id).image)
        flash("New question has been succesfully added")
        db.session.add(new_question)
        db.session.commit()
        return redirect(url_for('index'))

    else:
        return render_template('AddQuestion.html')


# In the index.html file, the entire question db will be displayed
# When the user clicks on view more btn, they would be redirected to the ParticularQuestion url
@app.route('/ParticularQuestion', methods=['GET', 'POST'])
def ParticularQuestion():
    if request.method == 'POST':
        id = request.args['questionid']
        username = User.query.get(session['user']).username
        image=User.query.get(session['user']).image
        print('question id is', id)
        new_response = Response(username=username,
                                description=request.form['description'],
                                pay=request.form['pay'], questionID=id, image=image)
        db.session.add(new_response)
        db.session.commit()
        return redirect(url_for('index'))
    else:
        args = request.args
        print('args in q url is', args)
        questionid = Question.query.get(args['questionid'])
        # To check whether the user view the q is same as the user who raised that question. If True, then display assign tag
        isSamePerson = args['user']
        print(isSamePerson)
        user = questionid.askedby_id
        img = User.query.get(user).image
        username = User.query.get(user).username
        response = Response.query.filter_by(questionID=questionid.id).all()
        print("response is", response)
        return render_template('ParticularQuestion.html', question=questionid, username=username, img=img,
                               response=response,
                               isSamePerson=isSamePerson)


################################ My Questions Section ###################################

@app.route('/DoubtSolved')
def DoubtSolved():
    id = request.args
    print(id)
    q = Question.query.get(id)
    print(q.status)
    q.status = 'Solved'
    print(q.status)
    db.session.commit()
    return render_template('DoubtSolved.html', q=q)


@app.route('/Delete')
def Delete():
    id = int(request.args['id'])
    print('to be deleted ', id)
    obj = Question.query.filter_by(id=id).one()
    db.session.delete(obj)
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/assign')
def assign():
    qid = int(request.args['qid'])
    assignedto_ID = int(request.args['userid'])
    createdbyId = session['user']
    print('to be assign ', id)
    obj = Question.query.filter_by(id=qid).one()
    print('obj is', obj)
    print(obj.question)
    obj.status = 'Assigned'
    assign = Assigned(createdbyId=createdbyId, questionID=qid, assignedto_ID=assignedto_ID,
                      assignedName=request.args['assignedName'], questionName=request.args['questionName'])
    db.session.add(assign)
    db.session.commit()
    print('************* STATUS CHANGED TO ASSIGNED **************')
    return redirect(url_for('index'))


####################################  OTHER ROUTES  #########################################


@app.route('/payment')
def payment():
    details = request.args
    print(details)
    mentor = str(details['doubt'])
    print('m is', mentor)
    amt = details['amount']
    user_id = session['user']
    u = User.query.get(user_id)
    mentor = User.query.filter_by(username=mentor).first()
    topay = User.query.get(mentor.id)
    print('mentor is  ', topay)
    if u.score > 0:
        flash("Payment successully made")
        print(u.score)
        u.score = u.score - int(amt)
        topay.score += int(amt)
        db.session.commit()
        return redirect(url_for('index'))
    else:
        return render_template('4o4.html', display_content="Transcation unsuccessul due to lack of credits")


@app.route('/verifiedskills', methods=['POST', 'GET'])
def verifiedskills():
    if request.method == 'POST':
        points = 0
        result = request.form
        r1 = result['q1']
        r2 = result['q2']
        r3 = result['q3']
        r4 = result['q4']
        r5 = result['q5']

        if r1 == 'C':
            points += 20
        if r2 == 'A':
            points += 20
        if r3 == 'C':
            points += 20
        if r4 == 'B':
            points += 20
        if r5 == 'B':
            points += 20

        if points >= 60:
            userid = session['user']
            user = User.query.filter_by(id=userid).one()
            user.verifiedskills = 'javascript'
            db.session.add(user)
            db.session.commit()
        return render_template('quizResult.html', points=points)

    return render_template('quiz.html')


######################################### Routes to display ####################################

@app.route('/scoreBoard')
def scoreBoard():
    rank_user = User.query.order_by(desc(User.score))
    return render_template('scoreBoard.html', rank_user=rank_user)


# Shows the user profile of the user who is currently logged in
@app.route('/profile')
def profile():
    userid = session['user']
    print('userid is', userid)
    Profile = User.query.filter_by(id=userid).one()
    return render_template('profile.html', i=Profile)


# Shows the list of tasks assigned to and by a particular user
@app.route('/history')
def history():
    user_id = session['user']
    askedByme = Assigned.query.filter_by(createdbyId=user_id).all()
    toBeDoneByMe = Assigned.query.filter_by(assignedto_ID=user_id).all()
    myQuestion = Question.query.filter_by(askedby_id=user_id).all()
    print(myQuestion)
    return render_template('history.html', askedByme=askedByme, toBeDoneByMe=toBeDoneByMe, myQuestion=myQuestion,
                           user_id=user_id)


# To display all the questions asked by the particular user
'''
@app.route('/myQuestion')
def myQuestion():
    user_id = session['user']
    myQuestion = Question.query.filter_by(askedby_id=user_id).all()
    print(myQuestion)
    return render_template('myQuestion.html', myQuestion=myQuestion, user_id=user_id)
'''


@app.route('/scratchcard')
def scratchcard():
    return render_template('scratchcard.html')


@app.route('/jobs', methods=['POST', 'GET'])
def jobs():
    userid = session['user']
    user = User.query.filter_by(id=userid).one()
    recruiter = Recruiter.query.all()
    print(recruiter)
    if request.method == 'POST':
        print('post')

        return redirect(url_for('index'))
    return render_template('jobs.html', user=user, recruiter=recruiter)


@app.route('/submitinterview')
def submitinterview():
    new_item = Interview(user_id=request.args['uid'], username=User.query.get(session['user']).username,
                         recruiter_id=request.args['rid'], recruitername=request.args['recruitername'],
                         userabout=User.query.get(session['user']).about)
    db.session.add(new_item)
    db.session.commit()
    return redirect(url_for('index'))


########################Recruiter ################################

@app.route('/Rindex')
def Rindex():
    rid = session['user']
    username = Recruiter.query.get(session['user']).username
    print('*' * 30)
    print('Recruiter, u ARE LOGGINED IN AS', username)  # All those print statments are for testing purpose. Ignore them
    print('*' * 30)
    flash("welcome {}".format(username))
    today = time.strftime("%m/%d/%Y")
    interview = Interview.query.filter_by(recruiter_id=rid).filter_by(status='Confirmed').order_by(Interview.date).all()

    return render_template('Rindex.html', interview=interview, today=today)


@app.route('/Rnotifications', methods=['POST', 'GET'])
def Rnotifications():
    rid = session['user']
    print(Interview.query.all())
    allInterview = Interview.query.filter_by(recruiter_id=rid).filter_by(status='Pending').all()
    print(allInterview)
    if request.method == 'POST':
        id = request.form['id']
        confirm_appointment = Interview.query.filter_by(id=id).one()
        confirm_appointment.status = 'Confirmed'
        confirm_appointment.date = request.form['date']
        confirm_appointment.time = request.form['time']
        db.session.commit()
        return redirect(url_for('Rindex'))
    return render_template('Rnotifications.html', allInterview=allInterview)


@app.route('/CancelInterview')
def CancelInterview():
    id = int(request.args['id'])
    print('to be cancelled ', id)
    CancelAppointment = Interview.query.filter_by(id=id).one()
    print(CancelAppointment)
    CancelAppointment.status = 'Denied'
    db.session.commit()
    return redirect(url_for('Rindex'))


######################################### MAIN ####################################


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
