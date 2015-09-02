import re

try:
    import urllib.parse as urlparse
except:
    import urlparse

camel_pat = re.compile(r'([A-Z])')
under_pat = re.compile(r'_([a-z])')

def camel_to_underscore(name):
    """Source: http://stackoverflow.com/a/17156414/4962672"""
    return camel_pat.sub(lambda x: '_' + x.group(1).lower(), name)

def underscore_to_camel(name):
    """Source: http://stackoverflow.com/a/17156414/4962672"""
    return under_pat.sub(lambda x: x.group(1).upper(), name)

def parse_project_name_from_repo_url(url, resource=None):
    """Get the project data from a repository url

    Receives the url for a resource in github/gitlab (maybe others)
    and parses the url to get the project name and namespace if available.

    If a resource is given (e.g. issues, commit), it checks on the position of the
    resource name on the url path to get the project name and namespace

    It returns a dictionary with the parts of the project name.
    """
    # Parse the url
    url = urlparse.urlparse(url)

    # Get the project data from the url
    parts = url.path.split('/')
    project = {}

    # If resource is given and it appears in url, then the repository has
    # a namespace name.
    if (resource and len(parts) >= 4 and parts[3] == resource) or \
        (resource and parts[2] != resource) or \
        (not resource and len(parts) >= 3):
        # Either the resource is in position 3
        # or is given but position 2 is the project name
        # or is not given and the path length is larger than 2
        project['namespace'] = parts[1]
        project['name'] = parts[2]
        project['longname'] = project['namespace'] + '/' + project['name']
        project['url'] = urlparse.urlunparse((url.scheme,
                                              url.netloc,
                                              '/%s/%s' % (project['namespace'], project['name']),
                                              None,
                                              None,
                                              None))
    else:
        # In other case the repo name is /<name>/<resource> or just /<name>
        project['name'] = parts[1]
        project['longname'] = project['name']
        project['url'] = urlparse.urlunparse((url.scheme,
                                              url.netloc,
                                              '/%s' % project['name'],
                                              None,
                                              None,
                                              None))

    return project
