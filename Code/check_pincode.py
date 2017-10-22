import xml.etree.cElementTree as ET
import re
import pprint
import string



filename = "Whitefield.osm"
wrong_postcodes = {}
all_postcodes = set()
for event, elem in ET.iterparse(filename, events=('start',)):
    if elem.tag == "way" or elem.tag == "node":

        subelem = elem.find('.tag[@k="addr:postcode"]')      #Check for the tag "addr:postcode" among the sub-tags for ways and nodes

        if subelem is None:
            continue
        else:
           postcode = subelem.attrib['v']
           all_postcodes.add(postcode) #identify all the unique postcode strings in the file
           postcode_num = "".join(re.findall('\d+',postcode)) # Preliminary Analysis of the all_postcodes set showed that certain post code strings contain white spaces in between. This expression captures all numerals and joins then without spaces
           if len(postcode_num)!=6: #A post code with length != 6 digits is erroneous
               print("elem_found")
               elem_detail = {}

#               elem_detail["name"]=elem.find('.tag[@k="name"]').attrib['v'] if elem.find('.tag[@k="name"]') is not None else ""
#               elem_detail["street"] = elem.find('.tag[@k="addr:street"]').attrib['v'] if elem.find('.tag[@k="addr:street"]') is not None else ""
               elem_detail["postcode"]=elem.find('.tag[@k="addr:postcode"]').attrib['v'] if elem.find('.tag[@k="addr:postcode"]') is not None else ""


               wrong_postcodes[elem.attrib['id']]=elem_detail # store the wrong postcodes in a dictionary with key as the id of the element with the wrong post code§   212\









