
import xml.etree.cElementTree as ET

filename = 'sample.osm'


## To print out street names##


#for event, elem in ET.iterparse(filename,events = ('end',)):
#	if elem.tag=='tag':
#        	if elem.attrib['k']=="addr:street":
#        		print elem.attrib['v']


## To print out postal code

#for event, elem in ET.iterparse(filename,events = ('end',)):
#	if elem.tag=='tag':
#        	if elem.attrib['k']=="addr:postcode":
#        		print elem.attrib['v']


# To print out city:

#for event, elem in ET.iterparse(filename,events = ('end',)):
#	if elem.tag=='tag':
#        	if elem.attrib['k']=="addr:city":
#        		print elem.attrib['v']


#To print out amenity:

for event, elem in ET.iterparse(filename,events = ('end',)):
	if elem.tag=='tag':
        	if elem.attrib['k']=="amenity":
        		print elem.attrib['v']


# To print out phone numbers:

#for event, elem in ET.iterparse(filename, events = ('end',)):
#	if elem.tag=='tag':
#        	if elem.attrib['k']=="phone":
#        		print (elem.attrib['v'])
