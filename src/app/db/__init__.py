from . import catalog
from . import schedule
from . import students
from . import popularity
from . import reviews


def update(update_courses=True, update_degrees=True, update_schedule=True, update_students=True, update_popularity=True, update_reviews=True):
    if update_courses:
        catalog.courses.update_db()

    if update_degrees:
        catalog.degrees.update_db()

    if update_schedule:
        schedule.update_db(newest_terms=5)
		
    if update_students:
        students.update_db()

    if update_popularity:
        popularity.update_db()

    if update_reviews:
        reviews.update_db()