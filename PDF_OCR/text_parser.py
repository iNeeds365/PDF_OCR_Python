import json
import re
import traceback
from entity import Company
from entity import Person
from entity import fix
import jsonpickle

areas = [x.lower() for x in ["Administration of Bodies Corporate", "Administrative Law", "Administrators of estates", "Adminstrators of deceased estates", "Adoptions", "Agency Work", "Agreements", "Alternate Dispute Resolution", "Antenuptial Contracts", "Anti-Trust: Competition", "Banking Law", "Body Corporate Management", "Broadcasting Law", "Building Law", "Business Agreements", "Business Law", "Business Rescue", "Business Transactions", "Civil Litigation", "Civil Mediation", "Commercial Advice", "Commercial Contracts", "Commercial Drafting", "Commerical Law", "Commissioner of Oaths", "Company Law", "Company Registrations", "Company Secretarial", "Competition Law", "Compliance Law", "Constitutional Law", "Construction Law", "Consumer Law", "Consumer Protection Law", "Contracts", "Contractual Law", "Conveyancers", "Conveyancing", "Corporate Commercial", "Corporate Governance", "Corporate Law", "Correspondent Work", "Credit Advice", "Credit Law", "Criminal Litigation", "Cross Border Negotiations", "Debt Collections", "Debt Recovery", "Debt Review", "Deseased Estates", "Deseased Estates Planning", "Development Law", "Disciplinary Enquiries", "Dispute Resolution", "Divorce Mediations", "Divorces", "Divorces", "Domestic Violence", "Drafting of Contracts", "Employment Law", "Energy Law", "Entertainment Law", "Estate Planning", "Estates", "Evictions", "Exchange Control", "Family Disputes", "Family Law", "Family-Child Mediation", "Financial Planning", "Franchising", "Freight Law", "General", "High & Magistrates' Court Civil Litigation", "High & Magistrates' Court Litigation", "High Court Litigation", "High, Magistrate's & Regional Court Litigation", "Housing Law", "Human Rights", "Immigration Law", "Insolvency", "Insurance Claims", "Insurance Law", "Intellectual Property Law", "International Trade", "Investigations", "Islamic Law", "Labour Dispute Resolutions", "Labour Law", "Labour Law", "Labour Law Specialists", "Land Claims", "Land Reformations", "Landlord Tenant Law", "Leases", "Legal Advisers", "Legal Consultants", "Levy Collections", "Liquidations", "Liquor Licensing", "Litigation", "Local Government Law", "Magistrates' Court Litigation", "Maintenance", "Maritime Law", "Matrimonial Law", "Media Law", "Mediation", "Mediators", "Medical Aid Law", "Medical Law", "Medical Negligence", "Mining Law", "Motor Insurance Law", "Municipal Law", "MVA", "Non-Profit Development", "Notaries", "Notary Public", "Pension Fund Law", "Personal Injury Claims", "Police Brutality", "Pro Bono", "Procurement", "Project Finance", "Property Law", "Property Transactions", "Public Law", "Real Estate", "Regional Court", "Rehabilitation", "Rent Tribunals", "Rental Collections", "Rental Law", "Rescission of Judgements", "Road Accident Fund Claims", "Sectional Title Law", "Sequestrations", "Small Business Law", "Sponsorship Law", "Sports Law", "Surrogacy Law", "Sworn Translator - German, English, Afrikaans-Legal", "Tax Litigation", "Technology Law", "Testamentary", "Testaments", "Third Party Claims", "Town Planning", "Trademarks", "Transfers", "Trusts", "Unlawful Arrests", "Valuers", "Water Law", "Wills", "Zoning of Properties"]]

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
        comp_data = comp_data.replace('http: / /', 'http://').replace('http / /', 'http://').replace('http: ', 'http:').replace(':/ /', '://').replace(' GPS: ', '. GPS: ').replace('https: / /', 'https://').replace('https / /', 'https://').replace('https: ', 'https:')
        comp_data = comp_data.replace('eMail :', 'eMail:').replace('e Mail:', 'eMail:')

        if comp_data.startswith('Nkosi'):
            comp_data = comp_data
        comp = Company()
        comp.Total = comp_data
        
        # company name
        regex = r"^[^\(]*\([^\)]*\)[ \t]*Inc"
        x = re.match(regex, comp_data)
        if x is None:
            regex = r"^[^\(]*"
            x = re.match(regex, comp_data)
        comp.CompanyName = x[0].strip()
        comp_data = comp_data[len(x[0]):]
        
        # persons or areas
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
                if x is not None and 'eMail:' not in x[0]:
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
        url_re = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        comp.Web = re.findall(url_re, comp_data)
        comp_data = re.sub(url_re, "", comp_data)

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
                email_txt = field[6:]
                comp.Email = re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", email_txt)
                email_txt = re.sub(r'[a-zA-Z\.]*@[a-zA-Z\.]*', '', email_txt)
                email_txt = re.sub(r'[\n\t ]+', '', email_txt)
                if len(email_txt) > 0:
                    comp.Note.append(email_txt)
            elif field.startswith('GPS:'):
                comp.GPS = field[4:]
            elif field.startswith('Docex'):
                comp.Docex = field[5:]
            else:
                comp.Address += field
        
        if len(comp.CompanyName) is 0 or (len(comp.Address) is 0 and comp.Note is None) or comp.Address.strip().startswith('('):
            return None
        return comp
    except Exception as e:
        print(str(e))
    return None

def parse_raw_txt_to_companies(txt):
    comp_data_list = []

    # Column break replacing
    txt = re.sub(r'\n+[^\n]*Copyright[^\n]*\n+', '\n', txt)
    # print(txt)

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