# coding=utf-8
#
#	script to open and close a piclinic session
#
#		Command line format:
#	        you_tube_stats.py api_key search_term
#
#
import sys
import requests
import json
import csv
from datetime import datetime
#
#   declare variables to access the YouTube API
#
you_tube_api_host = 'https://www.googleapis.com/youtube/v3/'
you_tube_search_url = you_tube_api_host + 'search'
you_tube_videos_url = you_tube_api_host + 'videos'


def print_search_csv (search_term,search_result):
    #
    # format selected fields as CSV and write to console
    #
    snippet_fields = [
        "publishedAt",
        "title",
        "description",
        "channelTitle",
        "channelId",
        "publishTime"
    ]
    csv_fields = [
        "searchTerm",
        "searchDate",
        "videoID",
        "publishedAt",
        "title",
        "description",
        "video",
        "channelTitle",
        "channelId",
        "publishTime"
    ]

    time_now = datetime.now()
    # dd/mm/YY H:M:S
    search_time = time_now.strftime("%d/%m/%Y %H:%M:%S")

    csvwriter = csv.writer(sys.stdout,
                            delimiter=',',
                            quotechar='"',
                            quoting=csv.QUOTE_MINIMAL)
    csvwriter.writerow(csv_fields)
    for item in search_result['items']:
        csv_row = []
        csv_row = [
            search_term,
            search_time,
            item['id']['videoId']
        ]
        for field in snippet_fields:
            csv_row.append(item['snippet'][field].encode('utf_8',errors='ignore').decode('ascii',errors='ignore'))
        csvwriter.writerow(csv_row)

def search_you_tube(api_key, search_term):
    #
    #    search YouTube for videos matching search_term
    #       success: return the number of videos found
    #       error: return NONE and display an error message to the console
    #
    return_value = 0
    #
    #   credential data to pass to session resource
    #
    search_data = {
        'key': api_key,
        'part': 'snippet',
        'maxResults': 50,
        'order': 'viewCount',
        'type': 'video',
        'relevanceLanguage': 'en',
        'q': search_term
    }
    #
    search_headers = {
        'Content-Type': 'application/json'
    }
    try:
        #
        #   Get the search results from YouTube
        #
        search_results = requests.get(you_tube_search_url, params=search_data, headers=search_headers)
        # if the request returned data, it should be a JSON string, so try to parse it
        # check for a response instead of a successful status code to catch and display
        # error responses as well as successful ones.
        if search_results.text:
            # print(search_results.text)
            # parse the response
            # if this doesn't work, the exception handler will catch it
            search_data = search_results.json()
            # format search data and print to console
            #print (json.dumps(search_data, indent = 4, separators = (',', ': ')))
            print_search_csv(search_term, search_data)
            #
            #   Get search result count
            #
            return_value = len(search_data['items'])

    except Exception as e:
        # if an exception was raised, get the message
        print(str(e))

    return return_value

'''
def close_session(token):
    #
    #   Close the piclinic session referenced by token
    #
    #       NOTE that the DELETE action requires only the token header
    #
    close_session_header = {
        'X-piClinic-token': token
    }

    try:
        session = requests.delete(piclinic_session_url, headers=close_session_header)
        if session.text:
            # if the request returned data, it should be a JSON string, so try to parse it
            session_data = session.json()
            if session_data['status']['httpResponse'] :
                delete_status = session_data['status']['httpResponse']
                # if there's an httpResponse, there's also an httpReason
                delete_response = session_data['status']['httpReason']

    except Exception as e:
        delete_status = 500
        delete_status = str(e)

    if delete_status != 200:
        # 200 = success, for anything else, show the reason.
        #  However, in most cases, either way the session is closed.
        #  either by this call or a previous one.
        #
        print("An error occurred closing the session.")
        print("Status : " + str(delete_status))
        print("Reason: " + delete_response)

    return # nothing
'''

def main(argv):
    #    Search YouTube using the credentials and search term passed in the command line

    api_key = None
    search_term = None

    # read the command line arguments
    if len(argv) > 2:
        # there are enough command line arguments to create the credentials
        api_key = argv[1]
        search_term = argv[2]
        # all others are ignored

    else:
        print("I couldn't search because you forgot to give me your api key and a search term.")
        return

    #  open a new session and get the token
    results = search_you_tube(api_key, search_term)
    if results:
        print("Videos found: " + str(results), file=sys.stderr)
    else:
        print("No videos found that match " + search_term, file=sys.stderr)
        return
    return

if __name__ == '__main__':
    main(sys.argv)
