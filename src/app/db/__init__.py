from . import catalog
from . import schedule
from . import students


def update(update_courses=True, update_degrees=True, update_schedule=True, update_students=True):
    if update_courses:
        catalog.courses.update_db()

    if update_degrees:
        catalog.degrees.update_db()

    if update_schedule:
        schedule.update_db(newest_terms=2)
		
    if update_students:
        students.update_db()
