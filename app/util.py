import re


camel_pat = re.compile(r'([A-Z])')
under_pat = re.compile(r'_([a-z])')

def camel_to_underscore(name):
    """Source: http://stackoverflow.com/a/17156414/4962672"""
    return camel_pat.sub(lambda x: '_' + x.group(1).lower(), name)

def underscore_to_camel(name):
    """Source: http://stackoverflow.com/a/17156414/4962672"""
    return under_pat.sub(lambda x: x.group(1).upper(), name)
