"""
user 1:  netid=netid1, 
should be in:
  uw_member
  uw_staff
  uw_affiliation_seattle-student-graduate
  uw_affiliation_graduate
  uw_alum
  uw_affiliation_alumni
  uw_affiliation_staff-employee
  uw_employee
  uw_student

note: id should be in uw_affiliation_alumni, uw_employee, 
      id should not be in uw_affiliation_bothell-student-undergraduate
"""
member = {
   'netid1': {
       "uw_member",
       "uw_staff",
       "uw_affiliation_seattle-student-graduate",
       "uw_affiliation_graduate",
       "uw_alum",
       "uw_affiliation_staff-employee",
       "uw_student",
       "uw_affiliation_bothell-student-undergraduate",
   },
}
