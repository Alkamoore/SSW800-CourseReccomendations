import os
import json

from flask import Flask, render_template, jsonify, abort, request
from werkzeug.local import LocalProxy
from flask_cors import CORS
from .context import get_db

flask_app = Flask(__name__)
mongo_client = LocalProxy(get_db)

from . import db
from .demos import demos
flask_app.register_blueprint(demos)
CORS(flask_app)


@flask_app.url_defaults
def hashed_static_file_url(endpoint, values):
    """


    :param endpoint:
    :param values:
    :return:

    source:
    https://gist.github.com/Ostrovski/f16779933ceee3a9d181

    """
    if 'static' == endpoint or endpoint.endswith('.static'):
        filename = values.get('filename')
        if filename:
            static_folder = flask_app.static_folder
            blueprint = endpoint.rsplit('.', 1)[0] if '.' in endpoint else request.blueprint
            if blueprint and flask_app.blueprints[blueprint].static_folder:
                static_folder = flask_app.blueprints[blueprint].static_folder
            filepath = os.path.join(static_folder, filename)
            if os.path.exists(filepath):
                values['_'] = int(os.stat(filepath).st_mtime)


def static_file_hash(filename):
    return int(os.stat(filename).st_mtime)


@flask_app.route('/')
def home():
    return render_template('index.html')

""" Course Information """
@flask_app.route('/api/courses/list')
def get_courses():
    """ List all courses in database """
    return jsonify(results=list(db.catalog.courses.get_all()))

@flask_app.route('/api/courses/tree')
def get_course_tree():
    """ List all courses in database in a tree """
    return jsonify(results=list(db.catalog.courses.get_tree()))
	
@flask_app.route('/api/courses/info')
def get_course_info():
    """ Get the course info for a specified course """
    letter = request.args.get('letter')
    number = request.args.get('number')

    if (letter is None) or (number is None):
        abort(400)

    r = mongo_client.catalog.courses.find_one({"letter": letter,
                                               "number": number},
                                              {'_id': False})

    if r is not None:
        return jsonify(r)

    abort(404)

""" Frequency Information """
@flask_app.route('/api/popularity/major')
def get_popular_for_major():
    """ List all courses in database in a tree """
    major = request.args.get('major')
	
    if (major is None):
        abort(400)
    	
    r = list(mongo_client.popularity.popularity.find({"required": 'false', "course": {'$regex': '^'+ major}}, {'_id': False}))

    if r is not None:
        return jsonify(r)

    abort(404)

@flask_app.route('/api/popularity/nonmajor')
def get_popular_for_nonmajor():
    """ List all courses in database in a tree """
    major = request.args.get('major')
	
    if (major is None):
        abort(400)
    	
    r = list(mongo_client.popularity.popularity.find({"course": {'$regex': '^'+ major}}, {'_id': False}))

    if r is not None:
        return jsonify(r)

    abort(404)

@flask_app.route('/api/popularity/rating')
def get_highest_rated():
    """ List all courses in database in a tree """
    major = request.args.get('major')
    
    if (major is None):
        abort(400)
    	
    c = str(list(mongo_client.reviews.reviews.find({"course": {'$regex': '^'+ major}}, {'course': 1, '_id': False}).sort([("course", 1)])))
    c = c.replace("'","")
    c = c.replace("{course: ","")
    c = c.replace("}, ",",")
    c = c.replace("}","")
    c = c.replace("[","")
    c = c.replace("]","")
    clist = c.split(",")
    cout = []
    seen = set()

    for i in clist:
        if i not in seen:
            cout.append(i)
            seen.add(i)

    r = []
    for c in cout:
        rtemp = str(list(mongo_client.reviews.reviews.find({"course": c}, {'rating': 1, '_id': False}).sort([("course", 1)])))
        rtemp = rtemp.replace("'","")
        rtemp = rtemp.replace("{rating: ","")
        rtemp = rtemp.replace("}, ",",")
        rtemp = rtemp.replace("}","")
        rtemp = rtemp.replace("[","")
        rtemp = rtemp.replace("]","")
        rlist = rtemp.split(",")
        rlist= list(map(int, rlist))
        r.append({"course": c , "rating": sum(rlist)/len(rlist)})

    r= list(sorted(r, key=lambda x: x['rating'], reverse=True))
    print(rtemp)
    print(rlist)
    print(cout)
    print(r)
    
    if r is not None:
        return jsonify(r)
    
    abort(404)

""" Student Information """
@flask_app.route('/api/students/tree')
def get_student_tree():
    """ List all courses in database in a tree """
    return jsonify(results=list(db.students.get_tree()))


@flask_app.route('/api/students/info')
def get_student_info():
    """ Get the student info for a specified course """
    cwid = request.args.get('cwid')

    if (cwid is None):
        abort(400)

    r = mongo_client.students.students.find_one({"cwid": cwid},
                                       {'_id': False})
    if r is not None:
        return jsonify(r)

    abort(404)

@flask_app.route('/api/students/req', methods=['POST'])
def get_required_courses():
    """ Get the student info for a specified course """
    post = request.get_json()
    cwid = str(post.get('cwid'))
    major = str(post.get('major'))
    
    if(major is None or cwid is None):
        abort(400)
    
    req = str(list(mongo_client.catalog.degrees.find({"id": major}, {"courseSet": 1, '_id': False})))
    tak = str(list(mongo_client.students.students.find({"cwid": cwid}, {"courses": 1, '_id': False})))
    rev = str(list(mongo_client.reviews.reviews.find({"cwid": cwid}, {"course": 1, '_id': False})))

    req = req[16:(len(req)-3)]
    tak = tak[14:(len(tak)-3)]
    req = req.replace("'","")
    tak = tak.replace("'","")
    req = req.replace(", ",",")
    tak = tak.replace(", ",",")
    rev = rev.replace("'","")
    rev = rev.replace("{course: ","")
    rev = rev.replace("}","")
    rev = rev[1:(len(rev)-1)]
    rev = rev.replace(", ",",")
    rlist = req.split(",")
    tlist = tak.split(",")
    qlist = rev.split(",")

    rreq = list(set(rlist).difference(set(tlist)))
    elec = list(set(tlist).difference(set(rlist)))
    arev = list(set(tlist).difference(set(qlist)))

    if rreq is not None and elec is not None:
        return json.dumps({"electives": elec, "remaining": rreq, "available": arev})

    abort(404)

""" Review Information """
@flask_app.route('/api/reviews/info')
def get_reviews():
    """ Get the reviews written by a specified student """
    cwid = request.args.get('cwid')

    if (cwid is None):
        abort(400)

    r = list(mongo_client.reviews.reviews.find({"cwid": cwid},
                                       {'_id': False}))
    if r is not None:
        return jsonify(r)

    abort(404)
	
@flask_app.route('/api/reviews/add', methods=['POST'])
def add_reviews():
    """ Add the reviews written by a specified student """
    post = request.get_json()
    cwid = str(post.get('cwid'))
    course = post.get('course')
    rating = post.get('rating')
    instructor = post.get('instructor')
    remarks = post.get('remarks')

    if (cwid is None or course is None):
        abort(400)
        
    r = mongo_client.reviews.reviews.insert_one ({"cwid": cwid,  "instructor": instructor,
                                                  "course": course, "rating": rating,
                                                  "remarks": remarks})
    
    if r is not None:
        return jsonify(status='OK',message='inserted successfully')

    abort(404)


""" Schedule Information """
@flask_app.route('/api/schedule/semesters', methods=['GET'])
def get_scheduled_semesters():
    """ List all semesters available in schedule database """
    # TODO: Sort properly and provide full semester name
    # ^ Possibly store this information in a separate collection
    return jsonify(results=list(db.schedule.get_semesters()))

@flask_app.route('/api/schedule/list')
def get_scheduled_courses():
    """ List all courses in database for a specified semester """
    return jsonify(results=list(db.schedule.get_tree(semester)))


@flask_app.route('/api/schedule/tree')
def get_scheduled_course_tree():
    """ List all courses in database for a specified semester in a tree """
    semester = request.args.get('semester')
    if semester is None:
        abort(400)
    return jsonify(results=db.schedule.get_tree(semester))


@flask_app.route('/api/schedule/combinations', methods=['POST'])
def get_scheduled_course_combinations():
    """ Get the course info for specified courses """
    semester = request.form.get('semester')
    call_numbers = request.form.getlist('call_numbers[]')
    if semester is None:
        abort(400)
    d = db.schedule.working_class_combinations_calendar(call_numbers=call_numbers, semester=semester)
    return jsonify(list(d))
