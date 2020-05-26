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
import re
import traceback
from datetime import datetime
#
#   declare variables to access the YouTube API
#
you_tube_api_host = 'https://www.googleapis.com/youtube/v3/'
you_tube_search_url = you_tube_api_host + 'search'
you_tube_videos_url = you_tube_api_host + 'videos'
you_tube_channels_url = you_tube_api_host + 'channels'


def format_iso8601_as_hms (iso8601_duration):
    # if string is not a duration, return it
    if iso8601_duration[:2] != 'PT':
        return iso8601_duration
    regex = 'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?'
    return_value = ''

    #
    #   parse the duration string
    duration_elements = re.match(regex, iso8601_duration)

    try:
        for digit in range (1,4):
            if (duration_elements.group(digit)):
                return_value = return_value + duration_elements.group(digit)
            else:
                return_value = return_value + '0'
            if (digit < 3):
                return_value = return_value + ":"
    except Exception as e:
        # return original string if an exception is raised
        return_value = iso8601_duration
        # if an exception was raised, get the message
        print(str(e), file=sys.stderr)
        print(traceback.format_exc(), file=sys.stderr)

    return return_value


def get_stats_for_channel (channel_id, channel_stats_data):
    #
    # return statistics for specified video from buffer
    #
    for channel in channel_stats_data['items']:
        if channel['id'] == channel_id:
            return channel
    # return none, if a matching channel is not found
    return None


def get_channel_stats (api_key, search_results):
    #
    # Get the channel stats for the videos returned in the search results
    #
    channel_ids_temp = []
    for item in search_results['items']:
        channel_ids_temp.append(item['snippet']['channelId'])
    # remove duplicate channel IDs
    channel_ids = list(dict.fromkeys(channel_ids_temp))
    #
    # query YouTube for the data
    #
    query_data = {
        'key': api_key,
        'part': 'statistics,brandingSettings',
        'id': ','.join(channel_ids)
    }
    #
    query_headers = {
        'Content-Type': 'application/json'
    }
    channel_stats_data = None
    try:
        #
        #   Get the data from YouTube
        #
        query_results = requests.get(you_tube_channels_url, params=query_data, headers=query_headers)
        # if the request returned data, it should be a JSON string, so try to parse it
        # check for a response instead of a successful status code to catch and display
        # error responses as well as successful ones.
        if query_results.text:
            # parse the response
            # if this doesn't work, the exception handler will catch it
            channel_stats_data = query_results.json()
            #
            #   check for errors
            if channel_stats_data['error']:
                print ("*** Error: " + str(channel_stats_data['error']['code']) +
                       ', ' + video_stats_data['error']['message'], file=sys.stderr)

    except Exception as e:
        # if an exception was raised, get the message
        print(str(e), file=sys.stderr)
        print(traceback.format_exc(), file=sys.stderr)

    return channel_stats_data


def get_stats_for_video (video_id, video_stats_data):
    #
    # return statistics for specified video from buffer
    #
    try:
        for video in video_stats_data['items']:
            if video['id'] == video_id:
                return video
    except Exception as e:
        print(str(e), file=sys.stderr)
        print(traceback.format_exc(), file=sys.stderr)
    # return none if no matching entry is found
    return None


def get_video_stats (api_key, search_results):
    #
    # Get the video stats for the videos returned in the search results
    #
    video_ids = []
    for item in search_results['items']:
        video_ids.append(item['id']['videoId'])
    #
    # query YouTube for the data
    #
    query_data = {
        'key': api_key,
        'part': 'statistics,contentDetails',
        'id': ','.join(video_ids)
    }
    #
    query_headers = {
        'Content-Type': 'application/json'
    }
    video_stats_data = None
    try:
        #
        #   Get the data from YouTube
        #
        query_results = requests.get(you_tube_videos_url, params=query_data, headers=query_headers)
        # if the request returned data, it should be a JSON string, so try to parse it
        # check for a response instead of a successful status code to catch and display
        # error responses as well as successful ones.
        if query_results.text:
            # parse the response
            # if this doesn't work, the exception handler will catch it
            video_stats_data = query_results.json()
            #
            #   check for errors
            if video_stats_data['error']:
                print ("*** Error: " + str(video_stats_data['error']['code']) +
                       ', ' + video_stats_data['error']['message'], file=sys.stderr)

    except Exception as e:
        # if an exception was raised, get the message
        print(str(e), file=sys.stderr)
        print(traceback.format_exc(), file=sys.stderr)

    return video_stats_data


def print_search_csv (api_key, search_term, search_results):
    #
    # format selected fields as CSV and write it to stdout
    #
    snippet_fields = [
        "title",
        "description",
        "channelTitle",
        "channelId"
    ]

    stats_fields = [
        "viewCount",
        "likeCount",
        "dislikeCount",
        "favoriteCount",
        "commentCount"
    ]

    content_fields = [
        "duration",
        "definition"
    ]

    channel_stats_fields = [
        "viewCount",
        "subscriberCount",
        "videoCount"
    ]

    csv_fields = [
        "searchTerm",
        "searchDate",
        "videoID",
        "videoUrl",
        "publishTime",
        "title",
        "description",
        "channelTitle",
        "channelId",
        "duration_ISO8601",
        "quality",
        "duration",
        "viewCount",
        "likeCount",
        "dislikeCount",
        "favoriteCount",
        "commentCount",
        "channelViews",
        "channelSubscribers",
        "channelVideos"
    ]

    time_now = datetime.now()
    # dd/mm/YY H:M:S
    search_time = time_now.strftime("%m/%d/%Y %H:%M:%S")

    #
    # get statistics for the videos & channels referenced in the search results
    #
    video_stats_data = get_video_stats (api_key, search_results)
    channel_stats_data = get_channel_stats(api_key, search_results)

    #
    #   write the results as a CSV file
    #
    csv_writer = csv.writer(sys.stdout,
                            delimiter=',',
                            quotechar='"',
                            quoting=csv.QUOTE_MINIMAL)
    csv_writer.writerow(csv_fields)
    for item in search_results['items']:
        csv_row = []    #init the row list
        #
        #   load the values for the video
        csv_row = [
            search_term,
            search_time,
            item['id']['videoId'],
            'https://www.youtube.com/watch?v=' + item['id']['videoId'],
            item['snippet']['publishedAt'].replace('T',' ').replace('Z','')
        ]
        #
        #   load the values from the search snippet object
        for field in snippet_fields:
            csv_row.append(item['snippet'][field].encode('utf_8',errors='ignore').decode('ascii',errors='ignore'))

        #
        #   load the values from the video's stats
        video_stats = get_stats_for_video(item['id']['videoId'], video_stats_data)
        #       first, those from the contentDetails object
        #       the exception handler should take care of any empty or missing objects
        for field in content_fields:
            try:
                csv_row.append(video_stats['contentDetails'][field])
            except:
                # if the field is missing, assign a value of 0
                csv_row.append("0")

        # then the formatted duration
        try:
            csv_row.append(format_iso8601_as_hms(video_stats['contentDetails']["duration"]))
        except Exception as e:
            # if an exception was raised, get the message
            print(str(e), file=sys.stderr)
            print(traceback.format_exc(), file=sys.stderr)
            # if the field is missing, assign a value of blank
            csv_row.append(" ")
        # csv_row.append("n/a")

        #
        #       then, those from the statistics object
        #       the exception handler should take care of any empty or missing objects
        for field in stats_fields:
            try:
                csv_row.append(str(video_stats['statistics'][field]))
            except:
                # if the field is missing, assign a value of 0
                csv_row.append("0")
        #
        #   load the channel data
        channel_stats = get_stats_for_channel(item['snippet']['channelId'], channel_stats_data)
        for field in channel_stats_fields:
            #       the exception handler should take care of any empty or missing objects
            try:
                csv_row.append(str(channel_stats['statistics'][field]))
            except:
                # if the field is missing, assign a value of 0
                csv_row.append("0")

        #   write this video's row of data
        csv_writer.writerow(csv_row)


def search_you_tube(api_key, search_term):
    #
    #    search YouTube for videos matching search_term
    #       success: return the number of videos found
    #       error: return NONE and display an error message to the console
    #
    return_value = 0
    #
    #   Set parameters for query.
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
            #
            #   check for errors
            if search_data['error']:
                print ("*** Error: " + str(search_data['error']['code']) +
                       ', ' + search_data['error']['message'], file=sys.stderr)
            else:
                #
                # no errors, so continue and
                # format search data and print to console
                #print (json.dumps(search_data, indent = 4, separators = (',', ': ')))
                print_search_csv(api_key, search_term, search_data)
                #
                #   Get search result count
                #
                return_value = len(search_data['items'])

    except Exception as e:
        # if an exception was raised, get the message
        print(str(e), file=sys.stderr)
        print(traceback.format_exc(), file=sys.stderr)

    return return_value


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
