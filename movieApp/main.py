from flask import Flask, render_template, request, json, session, flash
import http.client, random
from api_calls import *
from api_key import api_key
from list_of_actors import list_of_actors
from google.cloud import firestore
import hashlib

app = Flask(__name__)
app.secret_key = 'SUPER_RANDOM_STRING_OF_CHARACTERS_HERE'

@app.route('/')
def index():
	return render_template('home.html')

@app.route('/instructions')
def instructions():
	return render_template('instructions.html')

@app.route('/instructions2')
def instructions2():
	return render_template('alternate_path.html')

@app.route('/about')
def features():
	return render_template('about.html')

@app.route('/login')
def login():
	return render_template('login.html')

@app.route('/signup')
def signup():
	return render_template('signup.html')

@app.route('/confirmSignin')
def confirmSignin():
	return render_template('confirmSignin.html')

@app.route('/confirmSignup')
def confirmSignup():
	return render_template('confirmSignup.html')

@app.route('/create_user', methods=['POST', 'GET'])
def create_user():
    if request.method == 'GET':
        # Project ID is determined by the GCLOUD_PROJECT environment variable
        db = firestore.Client()
        doc_ref = db.collection(u'users').document(request.args.get('username'))
        entered_password = request.args.get('password')
        hashed_password = get_password_hash(entered_password)
        doc_ref.set({
            u'username': request.args.get('username'),
            u'password': hashed_password,
            u'points': 0
        })
    return render_template('confirmSignup.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash("Successfully logged out.")
    return render_template('home.html')

@app.route('/login_user', methods=['POST', 'GET'])
def login_user():
    if request.method == 'GET':
        db = firestore.Client()
        entered_username = request.args.get('username')
        entered_password = request.args.get('password')
        hashed_password = get_password_hash(entered_password)
        # Project ID is determined by the GCLOUD_PROJECT environment variable
        try:
            user_ref = db.collection(u'users').document(entered_username)
            user_password = user_ref.get().to_dict().get('password')
            user_score = user_ref.get().to_dict().get('points')
            if ( user_password == hashed_password):
                flash("Successfully logged in.")
                session['points'] = user_score
                session['username'] = entered_username
                return render_template('home.html')
            else:
                flash("Invalid username or password.")
                return render_template('login.html')
        except:
            flash("Invalid username or password.")
            return render_template('login.html')

def get_password_hash(pw):
    """This will give us a hashed password that will be extremlely difficult to 
    reverse.  Creating this as a separate function allows us to perform this
    operation consistently every time we use it."""

    encoded = pw.encode('utf-8')
    return hashlib.sha256(encoded).hexdigest()


@app.route('/game', methods = ['POST', 'GET'])
def game(): 
        return render_template('game.html', actorList=json.dumps(list_of_actors)) #may need to put API Key Back 

@app.route('/test1', methods=['GET', 'POST'])
def test1():
        print("This method has BEEN CALLED")
        myAPI=json.loads(request.data)
        api_request=myAPI.get("apiRequest")
        api_request=api_request.replace("INSERT", api_key)
        api_request= get_json(api_request)
        return json.dumps(api_request)

@app.route('/test2', methods=['GET', 'POST'])
def addPoints():
        print("called this function"); 
        db = firestore.Client()
        try:
            user_ref = db.collection(u'users').document(session['username'])
            user_score = user_ref.get().to_dict().get('points')
            user_score += 1
            data = {u'points': user_score}
            user_ref.update(data)
            session['points'] = user_score
            return "ok"
        except:
            return "ok"

        
def get_startActor():   
    request=get_popular("[API_KEY_HERE]")
    result=get_json(request)
    newNum=random.randint(0, len(result['results'])-1)
    actor=result['results'][newNum]['name']   
    STEP1ACTOR=actor 
    print(STEP1ACTOR)
    #GENERATING THE FIRST MOVIE 
    movie=result['results'][newNum]['known_for'][1]['id']
    STEP1MOVIE=result['results'][newNum]['known_for'][1]['title']   #STORE THIS IN THE GLOBAL VARIABLE
    print(STEP1MOVIE)
    #GET THE INFO FOR ANOTHER ACTOR
    anotherActor=get_info(movie, "[API_KEY_HERE]", STEP1ACTOR ) #RETURN TYPE IS AN ARRAY 
    STEP2ACTOR=anotherActor['name']
    print(STEP2ACTOR)

    #USE THIS INFORMATION TO GET INFO ABOUT A SECOND MOVIE
    #THE SECOND MOVIE CANT BE THE SAME AS THE FIRST ONE
    secondMovie=get_actor(anotherActor['id'])
    secondMovie=get_json(secondMovie)

    x=0
    while True:
        SECONDMovie=secondMovie['cast'][x]['id']
        STEP2MOVIE=secondMovie['cast'][x]['title']   #STORE THIS IN THE GLOBAL VARIABLE
        
        if STEP2MOVIE != STEP1MOVIE:
            break
        x+=1

    print(STEP2MOVIE)

    #USE THIS INFORMATION TO GET INFO ABOUT A THIRD ACTOR 

    anotherActor=get_info(SECONDMovie, "[API_KEY_HERE]", STEP2ACTOR)
    STEP3ACTOR=anotherActor['name']
    print(STEP3ACTOR)

    #GET THE THIRD MOVIE 
    thirdMovie=get_actor(anotherActor['id'])
    thirdMovie=get_json(thirdMovie)

    x=0
    while True: 
        THIRDMovie=thirdMovie['cast'][x]['id']
        STEP3MOVIE=thirdMovie['cast'][x]['title']

        if STEP3MOVIE != STEP2MOVIE:
            break

        x+=1

    print(STEP3MOVIE)

    #USE THIS INFORMATION TO GET INFO ABOUT A GOAL ACTOR 
    anotherActor=get_info(THIRDMovie, "[API_KEY_HERE]", STEP3ACTOR)
    STEP4ACTOR=anotherActor['name']
    print(STEP4ACTOR)

    return [actor, STEP4ACTOR]

app.jinja_env.globals.update(get_startActor=get_startActor) 

def getComparison(movie, start, end, goal):
    api_request=get_id(movie, "[API_KEY_HERE]")
    api_request=get_json(api_request)
    #print(api_request)

    if len(api_request['results']) > 0:
        movie_id=api_request['results'][0]['id']  #always pick the first movie
    else:
        return 0
    cast=get_cast(movie_id, "[API_KEY_HERE]" )
    cast=get_json(cast)
    #print(cast)

    finalActor=search_actor(end)
    finalActor=get_json(finalActor)
    
    if len(finalActor['results']) > 0: 
        end=finalActor['results'][0]['name'] 
    else: 
        return 0 


    x=0
    for people in cast['cast']:
        if people['name'].lower() == start.lower() or people['name'].lower() == end.lower(): 
            x+=1

    if x == 2:
        if end == goal:
         return 2
        else:
         return 1 

    else:
        return 0 




app.jinja_env.globals.update(getComparison=getComparison) 


@app.route('/gameProgress', methods = ['POST', 'GET'])
def gameProgress(): 
    if request.method == 'POST': 
        #get the form data for the movie and actor the user entered 
        result1=request.form.get('movie_name')
        result2=request.form.get('actor_name')
        strt=request.form.get('start-actor')
        sec=request.form.get('actor2')
        third=request.form.get('actor3')
        goal=request.form.get('goal-actor')
        path=request.form.get('validPath')
        count=request.form.get('count')
        count=int(count, 10)
        #print(count)

        #movie, start, end 
        if count == 1:
          i=getComparison(result1, strt, result2, goal)
        elif count == 2:
            i=getComparison(result1, sec, result2, goal)
        elif count == 3: 
            i=getComparison(result1, third, result2, goal)

        #print("Return Value:"+str(i))
        if i==2:
            db = firestore.Client()
            try:
                user_ref = db.collection(u'users').document(session['username'])
                user_score = user_ref.get().to_dict().get('points')
                user_score += 1
                data = {u'points': user_score}
                user_ref.update(data)
                session['points'] = user_score
                return render_template('winScreen.html')
            except:
                return render_template('winScreen.html')

        if i==1 and count==1:
            count=count+1 
            path=path+result1+"-->"+result2+"-->"
            return render_template('gameProgress.html', 
            startActor=strt, secondActor=result2,
            goalActor=goal, validMatch="Valid Match", path=path, counter=count)

        if i==1 and count==2:
            count=count+1 
            path=path+result1+"-->"+result2+"-->"
            return render_template('gameProgress.html', 
            startActor=strt, secondActor=sec, thirdActor=result2, 
            goalActor=goal, validMatch="Valid Match", path=path, counter=count)
        elif i==1 and count==3: 
            return render_template('loseScreen.html')
        else:
            return render_template('gameProgress.html', 
            result="", otherResult="", startActor=strt, secondActor=sec, thirdActor=third, 
            goalActor=goal, errorMsg="SORRY NOT A MATCH, TRY AGAIN", path=path, counter=count)

app.jinja_env.globals.update(gameProgress=gameProgress) 

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=8080, debug=True)
