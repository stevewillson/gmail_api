#!/usr/bin/python

#
# Gmail URL Downloader
# Steve Willson
# 7/29/18
# Given a search term, search for emails that match that query and attempt 
# to download the URLs included in that email  to the current directory 
# (files will be named file0..fileN)
# 

from __future__ import print_function
from apiclient.discovery import build
from apiclient import errors
from httplib2 import Http
from oauth2client import file, client, tools

# from the GetMessage functions
import base64
import email
from apiclient import errors

# for JSON printing of email objects
import json

# for regex searching
import re

# to download a file
import urllib2

# Search for a particular word in the subject and output those emails

SEARCH_QUERY = "subject:This is a test message"

# COPIED FROM GMAIL API EXAMPLE
def ListMessagesMatchingQuery(service, user_id, query=''):
    """List all Messages of the user's mailbox matching the query.

    Args:
        service: Authorized Gmail API service instance.
        user_id: User's email address. The special value "me"
        can be used to indicate the authenticated user.
        query: String used to filter messages returned.
        Eg.- 'from:user@some_domain.com' for Messages from a particular sender.

    Returns:
        List of Messages that match the criteria of the query. Note that the
        returned list contains Message IDs, you must use get with the
        appropriate ID to get the details of a Message.
        """
    try:
        response = service.users().messages().list(userId=user_id,
            q=query).execute()
        messages = []
        if 'messages' in response:
            messages.extend(response['messages'])

        while 'nextPageToken' in response:
            page_token = response['nextPageToken']
            response = service.users().messages().list(userId=user_id, q=query,
                pageToken=page_token).execute()
            messages.extend(response['messages'])

        return messages
    except errors.HttpError, error:
        print('An error occurred: %s' % error)

# COPIED FROM GMAIL API EXAMPLE
def GetMessage(service, user_id, msg_id):
    """Get a Message with given ID.

    Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    msg_id: The ID of the Message required.

    Returns:
    A Message.
    """
    try:
        message = service.users().messages().get(userId=user_id, id=msg_id).execute()

        #print('Message snippet: %s' % message['snippet'])

        return message
    except errors.HttpError, error:
        print('An error occurred: %s' % error)

# Setup the Gmail API

# Request READ only access to gmail
SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'
store = file.Storage('token.json')
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
    creds = tools.run_flow(flow, store)
service = build('gmail', 'v1', http=creds.authorize(Http()))

USER_ID="me"

messages = ListMessagesMatchingQuery(service, USER_ID, SEARCH_QUERY)

iter1 = 0
# Iterate through the messages and retrieve URLs
for message in messages:
    msg = GetMessage(service, USER_ID, message['id'])
    #print(msg)
    # Print out if debug mode is turned on... use -O to turn off debugging
    #if __debug__:
        #print(message['id'])
        #with open("json_out","w") as f:
            #json.dump(msg, f)

    pattern = r"(http|https)://([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?"
    for part in msg['payload']['parts']:
        # part 0 seems to be plaintext and part1 seems to be html -> need to verify
        value = part['body']['data'].encode('UTF8')
        search_str = base64.urlsafe_b64decode(value)
        #print(search_str)
       
        urls = re.finditer(pattern, search_str, re.DOTALL)
        print("Searching for all URLs")
        for url in urls:
            print(url.group(0))
            file_name = "file" + str(iter1)
            iter1 += 1
            # download the URLs from the email
            file_download = urllib2.urlopen (url.group(0))
            with open(file_name, 'wb') as output:
                output.write(file_download.read())

