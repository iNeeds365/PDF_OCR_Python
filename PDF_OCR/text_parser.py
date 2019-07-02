import json
import re
import traceback
from entity import Company
from entity import Person
from entity import fix
import jsonpickle

areas =[x.lower() for x in ['Administrative law', 'Advertising law', 'Admiralty law', 'Agency law', 'Alcohol law', 'Alternative dispute resolution', 'Animal law', 'Antitrust law', 'Competition law', 'Appellate practice', 'Art law', 'culture law', 'Aviation law', 'Banking law', 'Bankruptcy law', 'creditor debtor rights law', 'insolvency and reorganization law', 'Bioethics', 'Business law', 'commercial law', 'commercial litigation', 'Business organizations law', 'companies law', 'Civil law', 'common law', 'Class action litigation/Mass tort litigation', 'Common Interest Development law', 'Communications law', 'Computer law', 'Competition law', 'Conflict of law', 'private international law', 'Constitutional law', 'Construction law', 'Consumer law', 'Contract law', 'Copyright law', 'Corporate law', 'company law', 'corporate compliance law', 'corporate governance law', 'Criminal law', 'Cryptography law', 'Cultural property law', 'Custom law', 'Cyber law', 'Defamation', 'Derivatives law', 'futures law', 'Drug control law', 'Ecclesiastical law', 'Canon law', 'Elder law', 'Employee benefits law', 'Employment law', 'Energy law', 'Entertainment law', 'Environmental law', 'Equipment finance law', 'Family law', 'FDA law', 'Financial services regulation law', 'Firearm law', 'Food law', 'Franchise law', 'Gaming law', 'Health and safety law', 'Health law', 'HOA law', 'Immigration law', 'Insurance law', 'Intellectual property law', 'International law', 'International human rights law', 'International trade and finance law', 'Internet law', 'Juvenile law', 'Labour law', 'Labor law', 'Land use law', 'zoning law', 'Litigation', 'Martial law', 'Media law', 'Medical law', 'Mergers law', 'acquisitions law', 'Military law', 'Mining law', 'Music law', 'Mutual funds law', 'Nationality law', 'Native American law', 'Obscenity law', 'Oil law', 'gas law', 'Parliamentary law', 'Patent law', 'Poverty law', 'Privacy law', 'Private equity law', 'Private funds law', 'Hedge funds law', 'Procedural law', 'Product liability litigation', 'Property law', 'Public health law', 'Public International Law', 'Railway law', 'Real estate law', 'Securities law', 'Capital markets law', 'Social Security disability law', 'Space law', 'Sports law', 'Statutory law', 'Tax law', 'Technology law', 'Timber law', 'Tort law', 'Trademark law', 'Transport law', 'Transportation law', 'Trusts law', 'estates law', 'Utilities Regulation', 'Venture capital law', 'Water law', 'Conveyancers']]

def strip_(s):
    s = re.sub(r"^[^a-zA-Z0-9\(]*", '', s)
    s = re.sub(r"[^a-zA-Z0-9\)]*$", '', s)
    return s

def check_area(content):
    fields = content.split('; ')
    for field in fields:
        if field.strip().lower() in areas:
            return True
    return False

def parse_person_group(group_data):
    try:
        group = []
        for person_data in group_data:
            person = parse_person(person_data)
            if person is not None:
                group.append(person)
        return group
    except Exception as e:
        print(str(e))
        return None

def parse_person(person_data):
    try:
        p = Person()
        # email
        p.Email = [x[7:].strip() for x in re.findall(r"eMail: [^ ;]*", person_data)]
        person_data = re.sub(r"eMail: [^ ;]*", "", person_data)
        # cell
        p.Cell = [x[5:].strip() for x in re.findall(r"Cell [ \d/]*", person_data)]
        person_data = re.sub(r"Cell [ \d/]*", "", person_data)
        # tel
        p.Tel = [x[4:].strip() for x in re.findall(r"Tel [ \d/]*", person_data)]
        person_data = re.sub(r"Tel [ \d/]*", "", person_data)
        # fax
        p.Fax = [x[4:].strip() for x in re.findall(r"Fax [ \d/]*", person_data)]
        person_data = re.sub(r"Fax [ \d/]*", "", person_data)
        # tel
        p.Vax = [x[4:].strip() for x in re.findall(r"Vax [ \d/]*", person_data)]
        person_data = re.sub(r"Vax [ \d/]*", "", person_data)

        # degree and name
        fields = person_data.split(',')
        p.Name = fields[0]
        if len(fields) > 1:
            p.Degree = fields[1]

        return p
    except Exception as e:
        print(str(e))
        return None

def find_matching_paranthesis(x):
    ret = []
    op = 0
    st = 0
    for i in range(len(x)):
        if x[i] is '(':
            op += 1
            if op is 1:
                st = i
        elif x[i] is ')':
            op -= 1
            if op is 0:
                ret.append(x[st:i+1])
        elif x[i] not in ' \t,' and op is 0:
            break
    return ret

def parse_company(comp_data):
    try:
        # if comp_data.startswith('Bowman Gilfillan'):
        #     comp_data = comp_data
        comp = Company()
        comp.Total = comp_data
        regex = r"^[^\(]*"
        
        # company name
        x = re.match(regex, comp_data)
        comp.CompanyName = x[0].strip()
        
        # persons or areas
        comp_data = comp_data[len(x[0]):]
        contents = find_matching_paranthesis(comp_data)
        title = 'Principal'
        area_passed = False
        for con in contents:
            comp_data = comp_data.replace(con, '')
            con = con[1:-1]
            if check_area(con):
                area_passed = True
                fields = con.split('; ')
                for field in fields:
                    comp.Areas.append(field)
            elif con.startswith('see ') or area_passed:
                comp.Note.append(con)
            else:
                regex = r"^[^:;@\)]*:"
                x = re.match(regex, con)
                has_title = False
                if x is not None:
                    title = x[0].strip()[:-1]
                    con = con[len(x[0]):]
                    has_title = True
                fields = con.split('; ')

                person_data = []
                person_data_can = ''
                for field in fields:
                    if field.startswith('eMail') or field.startswith('Tel') or field.startswith('Fax') or field.startswith('Vax') or field.startswith('Cell'):
                        person_data_can += field
                    else:
                        if len(person_data_can) > 0:
                            person_data.append(person_data_can)
                        person_data_can = field
                if len(person_data_can) > 0:
                    person_data.append(person_data_can)

                for person in person_data:
                    p = parse_person(person)
                    p.Title = title
                    if '(Managing Partner)' in p.Name:
                        p.Name = p.Name.replace('(Managing Partner)', '')
                        p.Title = 'Managing Partner'
                        title = 'Partner'
                    
                    if p.Name.lower().strip().startswith('assisted by'):
                        p.Name = re.sub(r'assisted by', '', p.Name, flags=re.IGNORECASE)
                        p.Title = 'Assistant'
                    
                    title2 = re.findall('\([^\)]*\)', p.Name)
                    if len(title2) > 0:
                        p.Name = p.Name.replace(title2[0], '')
                        if has_title:
                            p.Title2 = title2[0][1:-1]
                        else:
                            p.Title = title2[0][1:-1]
                        
                    comp.Persons.append(fix(p))
                
        # company info
        comp_data = comp_data.replace('http: ', 'http:').replace(':/ /', '://').replace(' GPS: ', '. GPS: ')
        comp.Web = re.findall(r"(http:/[^ ]*)", comp_data)
        comp_data = re.sub(r"(http:/[^ ]*)", "", comp_data)

        # find note first
        note = re.findall('\([^\)]*\)', comp_data)
        if len(note) > 0:
            comp_data = comp_data.replace(note[0], ' ')
            comp.Note.append(note[0][1:-1])

        fields = [strip_(x) for x in comp_data.split('. ')]
        for field in fields:
            if field.startswith('Tel'):
                comp.Tel = field[4:]
            elif field.startswith('Cell'):
                comp.Cell = field[5:]
            elif field.startswith('P O Box'):
                comp.Postal = field
            elif field.startswith('Fax'):
                comp.Fax = field[4:]
            elif field.startswith('Vax'):
                comp.Vax = field[4:]
            elif field.startswith('eMail:'):
                comp.Email = field[6:]
            elif field.startswith('GPS:'):
                comp.GPS = field[4:]
            elif field.startswith('Docex'):
                comp.Docex = field[5:]
            else:
                comp.Address += field
        
        if len(comp.CompanyName) is 0 or len(comp.Address) is 0 or comp.Address.strip().startswith('('):
            return None
        return comp
    except Exception as e:
        print(str(e))
    return None

def parse_raw_txt_to_companies(txt):
    comp_data_list = []
    matches = re.finditer(r'\n\n([^\)\(])*\(', txt)
    for mat in matches:
        st = mat.start()
        en = txt.find('\n\n', st + 1)
        comp_data_list.append(txt[st+2:en])

    comp_data_list = [comp.replace('-\n','').replace('\n',' ') for comp in comp_data_list]

    companies = []

    if 0:
        comp = parse_company(comp_data_list[16])
        exit()

    for comp_data in comp_data_list:
        comp = parse_company(comp_data)
        if comp is not None:
            companies.append(fix(comp))

    return companies