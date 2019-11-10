import re
import json

class Company(object):

    def __init__(self):
        self.CompanyName = 'new company'
        self.Persons = []
        self.Address = ''
        self.Postal  = ''
        self.Tel = ''
        self.Cell = ''
        self.Fax = ''
        self.Vax = ''
        self.Docex = ''
        self.Web = []
        self.Email = []
        self.GPS = ''
        self.Areas = []
        self.Note = []
        self.Total = ''
        return

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)

class Person(object):
    def __init__(self):
        self.Name = 'new person'
        self.Degree = ''
        self.Title = ''
        self.Title2 = ''
        self.Tel = []
        self.Fax = []
        self.Vax = []
        self.Cell = []
        self.Email = []
        self.Note = []
        self.Assist = []

    
def fix(obj):
        regex = r"[\n\t ]+"
        for prop in vars(obj).keys():
            if not prop.startswith('_'):
                val = getattr(obj, prop)
                if type(val) is str:
                    val = re.sub(regex, " ", val).strip()
                    setattr(obj, prop, val)
        return obj
