
import csv
import codecs
import pprint
import re
import xml.etree.cElementTree as ET

import cerberus

import schema

import auditworking
import phonenumbers

OSM_PATH = "lowell.xml"

NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

SCHEMA = schema.schema

# Make sure the fields order in the csvs matches the column order in the sql table schema
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']


def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                  problem_chars=PROBLEMCHARS, default_tag_type='regular'):
    """Clean and shape node or way XML element to Python dict"""

    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []  # Handle secondary tags the same way for both node and way elements
    count = 0
    
    if element.tag == 'node':
        for node in node_attr_fields:
            #for each desirable node in the fields list
            node_attribs[node] = element.attrib[node]
            #add the node attrib to the dictionary
            
    if element.tag == 'way':
        for way in way_attr_fields:
            way_attribs[way] = element.attrib[way]
        
    for child in element:
        id = element.attrib['id']
        #the top level "node id" attribute
        
        if child.tag == 'tag':
            #for children with 'tag' tag
            if problem_chars.match(child.attrib['k']):
                continue
                #if tags with the 'k' attribute contain PROBLEMCHARS, skip to the next loop
            
            else:
                types = {}
                types['id'] = id
                types['value'] = child.attrib['v']
                #value: the tag "v" attribute
                
                if ':' in child.attrib['k']:
                    # if there's a colon in the 'k' attribute
                    loc = child.attrib['k'].find(":")
                    #find the location of the colon
                    key = child.attrib['k']
                    types['key'] = key[loc+1:]
                    types['type'] = key[:loc]
                    # if the tag 'k' value contains a ':', the characters before the ':' 
                    #should be set as the tag type, and the characters after should be set as the tag key
                
                

                 #cleaning function for 'addr:street'   
                if child.attrib["k"] == 'addr:street':
                    types['value'] = auditworking.update_name(child.attrib["v"], auditworking.mapping)
                       
                #cleaning function for 'phpne'
                if child.attrib["k"] == 'phone':
                    if phonenumbers.update_phone(child.attrib["v"]):
                        types['value'] = phonenumbers.update_phone(child.attrib["v"])
                    else: 
                        continue
                    
                else:
                    
                    types['key'] = child.attrib['k']
                    types['type'] = 'regular'
                
                tags.append(types)
                
        if child.tag == 'nd':
            nds = {}
            nds['id'] = id
            #top level element (way) id
            nds['node_id'] = child.attrib['ref']
            #node id : the ref attribute value of the nd tag
            nds['position'] = count
            #position: the index starting at 0 of the nd tag i.e. what order the nd tag appears within
            #the way element
            count += 1
            way_nodes.append(nds)
            
    
    
    print {'node': node_attribs, 'node_tags': tags}
    print {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}
    
    if element.tag == 'node':            
        return {'node': node_attribs, 'node_tags': tags}
               
    elif element.tag == 'way':
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}
                    



# ================================================== #
#               Helper Functions                     #
# ================================================== #
def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


def validate_element(element, validator, schema=SCHEMA):
    """Raise ValidationError if element does not match schema"""
    if validator.validate(element, schema) is not True:
        field, errors = next(validator.errors.iteritems())
        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        error_string = pprint.pformat(errors)
        
        raise Exception(message_string.format(field, error_string))


class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if isinstance(v, unicode) else v) for k, v in row.iteritems()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


# ================================================== #
#               Main Function                        #
# ================================================== #
def process_map(file_in, validate):
    """Iteratively process each XML element and write to csv(s)"""

    with codecs.open(NODES_PATH, 'w') as nodes_file, \
         codecs.open(NODE_TAGS_PATH, 'w') as nodes_tags_file, \
         codecs.open(WAYS_PATH, 'w') as ways_file, \
         codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file, \
         codecs.open(WAY_TAGS_PATH, 'w') as way_tags_file:

        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        validator = cerberus.Validator()

        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            if el:
                if validate is True:
                    validate_element(el, validator)

                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])


if __name__ == '__main__':
    # Note: Validation is ~ 10X slower. For the project consider using a small
    # sample of the map when validating.
    process_map(OSM_PATH, validate=True)
