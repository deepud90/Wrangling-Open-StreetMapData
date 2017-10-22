import xml.etree.cElementTree as ET
import re
import cerberus
import local_schema
import codecs
import csv
from change_street_address import modify_street_address
from change_street_address import create_full_address
from clean_phone_number import check_and_clean_number

NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"

SCHEMA = local_schema.schema


############# Parameter and regular expressions to modify street address  #################################################################


#end_words = ["Avenue","Circle","Colony","Cross","Lane","Main","Layout","Mall","Rd","Zone","EPIP Area","Road(?:\sno\.\s[1-9]|\s[1-9])?"]
end_words = ["Avenue","Circle","Colony","Cross","Lane","Main","Layout","Mall","Rd","Zone","EPIP Area","Road(\sno\.\s[1-9]|\s[1-9])?"] # List of end words to identify street types.
                                                                                                                                    # The last string captures strings  "Road, Roan No. 1, Road 1" etc.

# Create regular expression list for use later
expression = r"\b" + "({:s})".format('|'.join(end_words)) + r"\b" # Combine all the end words above into a single string using an 'or' condition. Will be used to generate the regular expression
reg_ex = re.compile(expression, re.IGNORECASE) #This regex shall be used to check addresses if they are in the right format.
re_len = re.compile(r'\w+') #regular expression to capture words. Will be used later to check the length of address strings in terms of the number of words contained in them
regex_phone = re.compile(r'1800') ### regular expression used to skip hotline numbers, while cleaning phone numbers (explained more in the documentation)

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')






# Dictionary of element ids with corrected pincodes, to be applied before writing out the data into CSV file
#The elements with problematic pincodes were identified separately using the subroutine "check_pincode.py". The only criteria applied to check for wrong pincodes was to see if their length was not equal to six digits
#There could be other errors (like wrong pincodes for a particular location), but they are much more difficult to locate. This criteria returned only a limited number of wrong pincodes,
# and hence we use the dictionary below to correct them. The dictionary keys are the element IDs and the values are the corrected pincode values that shall replace the existing pin code values.
pincodes = {"343138203":"560103","343138212":"560103","4447114330":"560109","4447418152":"560037","4487939369":"560066","4488807180":"560066","4489960691":"560066"}



NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']

def get_element(filename, tags=('node','way','relation')): #parse through the elements in the xml file
    context = ET.iterparse(filename,events=('start','end'))
    _, root = next(context) #get root element
    for event,elem in context:
        if elem.tag in tags and event =='end':
            yield elem
            root.clear()

def validate_element(element,validator,schema=SCHEMA):  # Check if the return value from shape element fits the required schema
    """Raise ValidationError if element does not match schema"""
    if validator.validate(element, schema) is not True:
        field, errors = next(validator.errors.iteritems())
        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        error_string = pprint.pformat(errors)

        raise Exception(message_string.format(field, error_string))


def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS, # This function has been designed as per instructions from Udacity. The instructions can be found in the appendix
                  problem_chars=PROBLEMCHARS, default_tag_type='regular',count_flag=0):# section of the code documentation. Note that the data cleaning is performed inside this function as well.
    """Clean and shape node or way XML element to Python dict"""

    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []  # Handle secondary tags the same way for both node and way elements

#*******************************************************************************************************************************************************************************
    if element.tag == 'node':
        for attr in NODE_FIELDS:
            node_attribs[attr] = element.attrib[attr]
        second_tags = element.findall('tag') #find all the second level tags of the node element
        element_id = element.attrib["id"]

        is_full_address = 0 # This variable is used later in case a new attribute (full address) is be added to describe those nodes having full address in the field for street addresses. Check the documentation

        for second_tag in second_tags:

            second_tag_attrib = second_tag.attrib

            if PROBLEMCHARS.search(second_tag_attrib["k"]):
                continue

##################################### BEGIN DATA CLEANING FOR NODE ELEMENT ##################################################################################

######### Modifying the street address attribute value #####################################################################################################


            if second_tag_attrib["k"]=="addr:street":

                (new_address,is_full_address) = modify_street_address(second_tag_attrib['v'], reg_ex,re_len) #details of this function given in documentation
                if is_full_address == 1:    ## If the street address attribute contained the entire location address instead of only street address (as is often found in this file), create a full address for the element.
                                            ## This new information regarding the new tag will be added after the current for loop (which iterates over all the element tags) will be completed.
                    full_address = create_full_address(element) # details of this function given in documentation.

                second_tag_attrib['v'] = new_address #replace with the "cleaned" address

######### Modifying the phone attribute value #############################################################################
            if second_tag_attrib["k"]=="phone":
                second_tag_attrib['v']=check_and_clean_number(second_tag_attrib['v']) #Details of this function given in documentation

######### Modifying the pincode attribute value ###########################################################################
            if second_tag_attrib["k"]=="addr:postcode":
                if element_id in pincodes:
                    second_tag_attrib["v"] = pincodes[element_id] # assign the corrected pincode. This dictionary pincodes is made at the beginning of thi file

###################################### END DATA CLEANING FOR NODE ELEMENT #################################################################################################################################################

            re_pattern = re.compile(r':')
            if (re_pattern.search(second_tag_attrib["k"])):

                second_tag_attrib["type"] = second_tag_attrib["k"].split(":")[0] # if tag 'k' value contains a ":", the characters before ":" is set as tag type
                second_tag_attrib["k"] = ":".join(second_tag_attrib["k"].split(":")[1:]) #if tag 'k' value contains a ":", the characters after ":" is set as tag key
            else:
                second_tag_attrib["type"] = "regular" # type is regular if no ":" is present

            second_tag_attrib["key"] = second_tag_attrib.pop("k") #renaming the dictionary key
            second_tag_attrib["value"] = second_tag_attrib.pop("v") #renaming the dictionary key
            second_tag_attrib["id"] = element_id
            tags.append(second_tag_attrib)

        if is_full_address == 1:         ### Add information about a new tag which contains the entire address ("addr:full" feature as per OpenStreetMap documentation). This will be added to the database
            attrib_new_second_tag = {"key":"full","type":"addr","value":full_address,"id":element_id}
            tags.append(attrib_new_second_tag)
            #print full_address



    elif element.tag == 'way':
        for attr in WAY_FIELDS:
            way_attribs[attr] = element.attrib[attr]
        element_id = element.attrib["id"]
        second_tags = element.findall('tag')

        is_full_address = 0 # This variable is used later in case a new attribute (full address) is be added to describe those ways having full address in the field for street addresses

        for second_tag in second_tags:

            second_tag_attrib = second_tag.attrib

            if PROBLEMCHARS.search(second_tag_attrib["k"]):
                continue
##################################### BEGIN DATA CLEANING FOR WAY ELEMENT #########################################################################################################################

######### Modifying the street address attribute value ##############################################################################################

            if second_tag_attrib["k"] == "addr:street":
                (new_address, is_full_address) = modify_street_address(second_tag_attrib['v'], reg_ex,re_len)
                second_tag_attrib['v'] = new_address

                if is_full_address == 1:  ## If the street address attribute contained the entire location address instead of just street address, create a full address for the element.
                                            ## This information regarding this new tag will be added at the end after this for loop which iterates over all the element tags will be completed.
                    full_address = create_full_address(element)


##################### Modifying the phone attribute value ###########################################################################
            if second_tag_attrib["k"] == "phone":
                second_tag_attrib['v'] = check_and_clean_number(second_tag_attrib['v'])

################### Modifying the pincode attribute value ###########################################################################
            if second_tag_attrib["k"] == "addr:postcode":
                if element_id in pincodes:
                    second_tag_attrib["v"] = pincodes[element_id]
###################################### END DATA CLEANING FOR WAY ELEMENT #############################################################################################################################

            re_pattern = re.compile(r':')
            if (re_pattern.search(second_tag_attrib["k"])):

                second_tag_attrib["type"] = second_tag_attrib["k"].split(":")[0] # if tag 'k' value contains a ":", the characters before ":" is set as tag type
                second_tag_attrib["k"] = ":".join(second_tag_attrib["k"].split(":")[1:]) #if tag 'k' value contains a ":", the characters after ":" is set as tag key
            else:
                second_tag_attrib["type"] = "regular" # type is regular if no ":" is present

            second_tag_attrib["key"] = second_tag_attrib.pop("k") #renaming the dictionary key
            second_tag_attrib["value"] = second_tag_attrib.pop("v") #renaming the dictionary key
            second_tag_attrib["id"] = element_id
            tags.append(second_tag_attrib)

        if is_full_address == 1:         ### Addition of information about a new tag which contains the entire address ("addr:full") feature as per OpenStreetMap documentation). This will be added to the database
            attrib_new_second_tag = {"key": "full", "type": "addr", "value": full_address, "id": element_id}
            tags.append(attrib_new_second_tag)




        second_nds = element.findall('nd')

        pos = 0
        for second_nd in second_nds:
            second_nd_attrib = second_nd.attrib
            second_nd_attrib["id"] = element_id
            second_nd_attrib["node_id"] = second_nd_attrib.pop("ref")
            second_nd_attrib["position"] = pos
            pos += 1
            way_nodes.append(second_nd_attrib)

    if element.tag == 'node':
        node_dict =  {'node': node_attribs, 'node_tags': tags}
        #print node_dict
        return {'node': node_attribs, 'node_tags': tags}
    elif element.tag == 'way':
        way_dict = {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}

        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}
#*******************************************************************************************************************************************************************************

class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if isinstance(v, unicode) else v) for k, v in row.iteritems()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)



def process_map(file,validate):
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

        for elem in get_element(file,tags=("node","way")):
            el = shape_element(elem)
            if el:
                if validate is True:
                    validate_element(el,validator)

                if elem.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])

                elif elem.tag == 'way':

                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])


if __name__ == '__main__':

    process_map("../Whitefield.osm",validate=False)



