""" Interface with the existing Stevens Institute Course Scheduler """
from datetime import datetime, timedelta
import re
import urllib.request
from xml.dom import minidom

__author__ = "Constantine Davantzis & Alexis Moore"
__status__ = "Complete"

# Compile regular expression to find terms in XML response.
re_terms = re.compile(r'<Term Code="(.*)" Name="(.*)"/>')
# Compile regular expression to match parts of course section
re_section = re.compile(r'(?P<prefix>[a-zA-Z]+)\s?(?P<number>\d+)(?P<code>\S+)')


def terms():
    """ Get Term Information
    :returns: A list of term codes and names
    :rtype: list
    """
    t = list()
    f = urllib.request.urlopen("https://web.stevens.edu/scheduler/core/core.php?cmd=terms")
    for  term in minidom.parse(f).getElementsByTagName("Term"):
        t.append(term.getAttribute('Code'))

    return t


def courses(term):
    """ Get Course Information
    :param term: The selected school term.
    :returns: A generator yielding course information for selected term
    :rtype: generator
    """
    print(term)
    f = urllib.request.urlopen('https://web.stevens.edu/scheduler/core/core.php?cmd=getxml&term='+term)
    for course in minidom.parse(f).getElementsByTagName("Course"):
        # Basic Course Information
        c = {"_id": course.getAttribute('CallNumber'),
             "title": course.getAttribute('Title'),
             "status": course.getAttribute('Status'),
             "section": re_section.match(course.getAttribute('Section')).groupdict(),
             'max_enrollment': int(course.getAttribute('MaxEnrollment')),
             'current_enrollment': int(course.getAttribute('CurrentEnrollment')),
             'instructor_1': course.getAttribute('Instructor1'),
             'instructor_2': course.getAttribute('Instructor2'),
             "meetings": [],
             'requirements': []}

        # Course Meeting Information
        for meeting in course.getElementsByTagName("Meeting"):
            m = {'day': meeting.getAttribute('Day'),
                 'site': meeting.getAttribute('Site'),
                 'building': meeting.getAttribute('Building'),
                 'room': meeting.getAttribute('Room'),
                 'activity': meeting.getAttribute('Activity')}
            if meeting.hasAttribute('StartTime') and meeting.hasAttribute('EndTime'):
                m.update({
                    "start_time": datetime.strptime(meeting.getAttribute('StartTime')[:-4], "%H:%M")+timedelta(hours=5),
                    "end_time": datetime.strptime(meeting.getAttribute('EndTime')[:-4], "%H:%M")+timedelta(hours=5)
                })
            c["meetings"].append(m)

        # Course Requirement Information
        for requirement in course.getElementsByTagName("Requirement"):
            c["requirements"].append({"control": requirement.getAttribute('Control'),
                                      "argument": requirement.getAttribute('Argument'),
                                      "value_1": requirement.getAttribute('Value1'),
                                      "operator": requirement.getAttribute('Operator'),
                                      "value_2": requirement.getAttribute('Value2')})

        # Course Activity Information - To be used to group specific types of classes
        c["activity"] = c["section"]["code"] if len(c["meetings"]) == 0 else c["meetings"][0]['activity']

        yield c
