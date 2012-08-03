# coding=utf8

import xml.etree.ElementTree as etree
import re

struct_template = """
class {class_name}(TOPObject):
    \"\"\" {doc}
    \"\"\"
    FIELDS = {{
        {fields}
    }}

"""

api_template = """
class {class_name}(TOPRequest):
    \"\"\" {doc}
    \"\"\"
    REQUEST = {{{requests}}}

    RESPONSE = {{{responses}}}

    API = '{api_string}'

"""

tree = etree.parse('ApiMetadat.xml')
root = tree.getroot()

def gen_structs():
    struct_file = open('pytop/topstruct.py', 'w', encoding='utf8', newline='\n')
    struct_base_file = open('struct_base.py', encoding='utf8')
    struct_file.write(struct_base_file.read())
    struct_base_file.close()
    for struct in root.find('structs'):
        class_name = struct.find('name').text
        doc = '%s\n\n    ' % struct.find('desc').text
        props = struct.find('props')
        fields = []
        docs = []
        for prop in props:
            prop_name = prop.find('name').text
            prop_type = prop.find('type').text
            prop_level = prop.find('level').text
            prop_desc = re.sub(r'\s*\n\s*', '\n        ', str(prop.find('desc').text).strip())
            is_list = prop_level.endswith('Array')
            #fields.append('\'%s\': \'%s\'' % (prop_name, prop_type))
            fields.append('\'%s\': {\'type\': \'%s\', \'is_list\': %s}' % (prop_name, prop_type, is_list))
            docs.append('@field %s(%s%s): %s' % (prop_name, prop_type, is_list and ', list' or '', prop_desc))
        fields = ',\n        '.join(fields)
        doc = doc + '\n    '.join(docs)
        struct_file.write(struct_template.format(class_name=class_name, doc=doc, fields=fields))
    struct_file.close()

def gen_apis():
    import pytop.topstruct as topstruct
    api_file = open('pytop/topapi.py', 'w', encoding='utf8', newline='\n')
    api_base_file = open('api_base.py', encoding='utf8')
    api_file.write(api_base_file.read())
    api_base_file.close()
    log = open('log.txt', 'w', encoding='utf8', newline='\n')
    for api in root.find('apis'):
        requests = []
        responses = []
        docs = []
        doc = [re.sub(r'\s*\n\s*', '\n        ', str(api.find('desc').text).strip())]
        api_string = api.find('name').text
        class_name = '%sRequest' % ''.join([item.capitalize() for item in api_string.split('.')[1:]])
        for response in api.find('response'):
            response_name = response.find('name').text
            response_type = response.find('type').text
            response_level = response.find('level').text
            response_desc = re.sub(r'\s*\n\s*', '\n        ', str(response.find('desc').text).strip())
            is_list = response_type.endswith('Array')
            docs.append('@response %s(%s%s): %s' % (response_name, response_type, is_list and ', list' or '', response_desc))
            responses.append("'%s': {'type': topstruct.%s, 'is_list': %s}" % (response_name, response_type, is_list))
        docs and doc.append('\n    '.join(docs))
        docs = []
        responses = responses and '\n        %s\n    ' % ',\n        '.join(responses) or ''
        for request in api.find('request') or []:
            request_name = request.find('name').text
            request_type = request.find('type').text
            if request_type.startswith('Field'):
                request_type = 'FieldList'
            elif request_type.startswith('byte'):
                request_type = 'Image'
            request_required = request.find('required').text
            is_required = request_required == 'required'
            request_desc = re.sub(r'\s*\n\s*', '\n        ', str(request.find('desc').text).strip())
            default = request.find('default')
            if default!=None:
                default = set(re.split(r'[\s,]+', str(default.text).strip()))
            optional = request.find('optional')
            if optional!=None:
                optional_temp = topstruct.Set()
                for item in re.split(r'[\s,]+', str(optional.text).strip()):
                    item_split = item.split('.')
                    if re.match(r'^[A-Z]', item_split[-1]):
                        optional_temp.update(['.'.join(item_split[:-1]+[key]) for key in topstruct.__dict__[item_split[-1]].FIELDS.keys()])
                    else:
                        optional_temp.add(item)
                optional = optional_temp
            requests.append("'%s': {'type': topstruct.%s, 'is_required': %s%s%s}" % (request_name, request_type, is_required, optional and ", 'optional': topstruct.%s" % optional or '', default and ", 'default': %s" % default or ''))
            docs.append('@request %s(%s): (%s)%s' % (request_name, request_type, request_required, request_desc))
        docs and doc.append('\n    '.join(docs))
        doc = '\n\n    '.join(doc)
        docs = []
        requests = requests and '\n        %s\n    ' % ',\n        '.join(requests) or ''

        api_file.write(api_template.format(class_name=class_name, doc=doc, requests=requests, responses=responses, api_string=api_string))
    api_file.close()
    log.close()



if __name__ == '__main__':
    gen_structs()
    gen_apis()
