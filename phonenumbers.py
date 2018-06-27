import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint

OSMFILE = "lowell.xml"


#Problematic characters in. phone numbers
phone_problems = ["+1", "(", ")", " "]



#Searches for any problemeatic characters in the phone number, if any exist, the number is added to the list
def audit_phone(phone_numbers, phone_digits):
   
    
	if any(x in phone_digits for x in phone_problems):
	    phone_numbers.append(phone_digits)


# Returns the number if the attribute has the key "phone"
def is_phone(elem):
    return (elem.attrib['k'] == "phone")



#Iterates through each element, determines if tag is a phone number, if it is it checks if there are problematic characters, if so, add to list
def phone(osmfile):
    osm_file = open(osmfile, "r")
    phone_numbers = []
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_phone(tag):
                    audit_phone(phone_numbers, tag.attrib['v'])
    osm_file.close()
    return phone_numbers


# If there are any problematic numbers, update the phone number to the standard format
def update_phone(number):

	if any(x in number for x in phone_problems):
		
		number = number.lstrip("'+1'").replace('(', '').replace(')', '')
		if number[0]==" " or number[0]=="-":
			number=number.lstrip("'', '-'")
			number=number.lstrip("-")
		number=number.replace(" ", "-")
		if number[7] != "-":
			number = number[:7] + '-' + number[7:]

	return number



def test():
    ph_numbers = phone(OSMFILE)    
    pprint.pprint(ph_numbers)

    for number in ph_numbers:
		print update_phone(number)



test() 