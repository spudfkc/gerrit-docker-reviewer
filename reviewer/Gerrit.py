import json
import urllib2

class Gerrit:
    _url_openreviews = 'changes/?q=status:open+reviewer:self&o=CURRENT_REVISION'

    def __init__(self, url, username, apikey):
        self.url = url
        self.username = username
        self.apikey = apikey

    def _gerrit_request(self, url):
        '''
        Handles making an HTTP request to a Gerrit server
        '''
        ### set up http/auth stuff
        passwdMan = urllib2.HTTPPasswordMgrWithDefaultRealm()
        passwdMan.add_password(None, url, self.username, self.apikey)

        authHandler = urllib2.HTTPDigestAuthHandler(passwdMan)
        opener = urllib2.build_opener(authHandler)
        urllib2.install_opener(opener)
        pagehandle = urllib2.urlopen(url)

        body = pagehandle.read()
        try:
            j = json.loads(body)
        except ValueError:
            # Gerrit doesn't return valid json
            j = json.loads(body[4:])
        return j

    def get_open_reviews(self):
        '''
        Gets all CURRENT REVISIONS of OPEN reviews that your user is a reviewer for.

        Returns json object of reviews
        '''
        url = ''.join([self.url, self._url_openreviews])
        return self._gerrit_request(url)

    def get_change(changeId):
        pass
