"""
user 1:  netid=netid1, sno=000100001, advanceid=0000400001 uwhr=870000001
affiliations:
  uw_member
  uw_staff
  uw_affiliation_seattle-student-graduate
  uw_affiliation_graduate
  uw_alum
  uw_affiliation_alumni
  uw_affiliation_staff-employee
  uw_employee
  uw_student
"""
person = {
   "netid1": {
       "netid": "netid1",
       "identifiers": {"sdb": "/person/sdb/000100001", "advance": "/person/advance/0000400001", "uwhr": "/person/uwhr/870000001"},
       "categories": [
            {"category_code": "1", "status_code": "3"},
            {"category_code": "2", "status_code": "1"},
            {"category_code": "2", "status_code": "3"},
            {"category_code": "4", "status_code": "1"},
            {"category_code": "4", "status_code": "3"},
            {"category_code": "14", "status_code": "3"},
            {"category_code": "16", "status_code": "1"},
            {"category_code": "19", "status_code": "3"},
            {"category_code": "20", "status_code": "3"},
            {"category_code": "28", "status_code": "1"},
            {"category_code": "30", "status_code": "1"},
            {"category_code": "36", "status_code": "1"},
            {"category_code": "42", "status_code": "1"},
            {"category_code": "49", "status_code": "1"},
            {"category_code": "62", "status_code": "1"},
            {"category_code": "64", "status_code": "1"},
            {"category_code": "89", "status_code": "1"},
            {"category_code": "102", "status_code": "1"},
            {"category_code": "123", "status_code": "1"},
            {"category_code": "124", "status_code": "1"},
            {"category_code": "140", "status_code": "1"},
            {"category_code": "154", "status_code": "1"},
            {"category_code": "176", "status_code": "1"},
            {"category_code": "177", "status_code": "1"},
       ],
   },
   "regid4": {
       "netid": "netid4",
       "identifiers": {"sdb": "/person/sdb/000100001", "sponsored": "/person/sponsored/0000400003", "uwhr": "/person/uwhr/870000001"},
       "categories": [
            {"category_code": "1", "status_code": "3"},
       ],
   }
}

uwnetid = {
    "regid1": {
        "uwnetid": "netid1",
        "validid": "870000001",
        "disenfran": "",
    },
    "regid2": {
        "uwnetid": "netid2",
        "validid": "870000002",
        "disenfran": "1",
    },
    "regid3": {
        "uwnetid": "netid3",
        "validid": "870000001",
        "disenfran": "",
    },
}

subscription = {
    "netid3": {
        "uwnetid": "netid3",
        "subscription": 60,
    },
    "regid4": {
        "uwnetid": "netid4",
        "subscription": 0,
    },
}

# matches 'regid3'
sponsored = {
    "0000400003": {
        "status_code": '1',
        "pac": '',
        "fname": "Joe",
        "lname": "Blow",
        "contact_email": ["joeblow@nowhere.com"],
    }
}

# matches 'regid3'
pac = {
    "0000400003": {
        "source": "sponsored",
        "status_code": '1',
        "pac": 'pbCx6e',
        "expiration": "2020-04-19 15:38:02",
        "message": "Pac set",
    }
}


pds = {
   "netid1": {
       "netid": "netid1",
       "edupersonaffiliation": ["member", "student", "alum", "staff", "employee"],
    }
}

sdb = {
    "000100001": {
        "netid": "netid1",
        "validid": "000100001",
        "studentid": "100001",
        "pac": "P",
        "categories": [{"category_code": "2", "category_name": "Graduate"}],
        "college": "X",
        "department": "LAW",
        "sdb_class": "12",
        "sdb_status": "E",
        "branch": "0",
        "source_code": "2",
        "source_name": "UW Students",
        "status_code": "1",
        "status_name": "Current",
    },
}

advance = {
    "0000400001": {
        "validid": "0000400001",
        "studentid": "1000001",
        "categories": [
            {"category_code": "16", "category_name": "Alumni"},
            {"category_code": "28", "category_name": "Development Affiliate"}
        ],
        "alumni_member": "N",
        "alumni_type": "AL",
        "source_code": "7",
        "status_code": "1",
    },
}

member = {
    "netid1": {
        "uw_member",
        "uw_staff",
        "uw_affiliation_seattle-student-graduate",
        "uw_affiliation_graduate",
        "uw_alum",
        "uw_affiliation_alumni",
        "uw_affiliation_staff-employee",
        "uw_employee",
        "uw_student",
    },
}
