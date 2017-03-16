# SSW800 - Course Recommendation Project Documentation
**Documentation**
-------------

Project:
--------
 - Project Cloned From: https://github.com/CDavantzis/SSW690-Project
 - Project Can Be Forked From: https://github.com/Alkamoore/SSW800-CourseReccomendations

Objective:
----------
Develop course recommendation software to assist members of the Stevens community with the course selection process by allowing them to see what courses they would enjoy or in the case of faculty, suggest to students based on their course history. 

New Features:
---------
- Student Selection
	 - Select who you are based on name/cwid
- Recommendation System 
	 - Review courses taken
	 - Recommend Course to Others

Features from C. Davantzis SSW690 Project:
---------

 - Background process that is linked to university registration system
	 - Able to download course information
	 - Class name, Time, Occupancy
 - Course Information
	 - Displays name, relevant description, course number
	 
Running Notes
---------
The database can be populated from the command line by using update_db.py --courses --degrees --schedule --students

Note, due to privacy concerns the student.json has not been uploaded. Instead create your own using the following format 

  { 
    "name" : "John Smith",
    "cwid" : "12345678",
	"advisor" : "Jane Doe",
	"major" : "SSE",
    "courses" : [
      [ 
		"SSW 540",
		"SSW 555"
      ]
    ]
  }


Requirements
---------
	Local installation mongodb
	Flask 
	Python 3+
