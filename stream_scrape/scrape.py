from playwright.sync_api import sync_playwright
import requests
from client_secrets import *
import sys

#Declare Variables
token_url = 'https://accounts.spotify.com/api/token'
base_url = 'https://api.spotify.com/v1/search?q=remaster%20'

#Send response for Spotify Token
def callToken():

	spotify_parameters = {"client_id" : client_ID, #Use your client ID provided by Spotify DEV
                          "client_secret" : client_secret, #Use your client secret provided by Spotify DEV
                          "grant_type" : "client_credentials"}
	
	token_response = requests.post(token_url, spotify_parameters)
	token_data = token_response.json()

	dataInput(token_data)

#Gets the artist and track name from the user
def dataInput(token_data):

	artist_name = input('Please Enter the Artist Name: ')
	track_name = input('Please Enter the Track Name: ')

	artist_name = artist_name.replace(" ", "+")
	track_name = track_name.replace(" ", "+")

	callURL(token_data, artist_name, track_name)

#Send API request for relevant artists
def callURL(token_data, artist_name, track_name):

	#Dictionaries contain information required for API request
	headers = {
		'Authorization': 'Bearer {token}'.format(token=token_data['access_token']),
		'Content-Type': 'application/json'
	}

	params = {
		'type': 'track,artist',
		'grant_type' : 'client_credentials',
		'limit' : '10',
		'offset' : '5'
	}

	#Sends request and recieves response in JSON format
	strURL = "https://api.spotify.com/v1/search?query=%2520track%3a" + track_name + "%2520artist%3A" + artist_name + "&type=track%2Cartist&&offset=0&limit=20"
	r = requests.get(strURL, headers=headers, params=params)
	jsonData = r.json()

	findURL(jsonData)

def findURL(jsonData):
	global url

	response_dict1 = jsonData['tracks']
	response_dict2 = response_dict1['items']
	response_dict3 = response_dict2[0]
	response_dict4 = response_dict3['external_urls']
	url = response_dict4['spotify']

	

#Calls the first function
callToken()

with sync_playwright() as p:
	def handle_response(response):
		#Breaks down JSON structure to find required information
		if ("/pathfinder/v1/query?operationName=queryAlbumTracks" in response.url):
			spotify_dict = response.json()
			
			spotify_dict1 = spotify_dict['data']
			spotify_dict2 = spotify_dict1['album']
			spotify_dict3 = spotify_dict2['tracks']
			spotify_dict4 = spotify_dict3['items']
			spotify_dict5 = spotify_dict4[0]
			spotify_dict6 = spotify_dict5['track']
			spotify_total = spotify_dict6['playcount']

			print(spotify_total)
			sys.exit()
		
		elif ("/query?operationName=getTrack&variables" in response.url):
			spotify_dict = response.json()
			
			spotify_dict1 = spotify_dict['data']
			spotify_dict2 = spotify_dict1['trackUnion']
			spotify_total = spotify_dict2['playcount']

			print(spotify_total)
			sys.exit()

	#Change False to True to hide the browser on launch
	browser = p.chromium.launch(headless=False) 
	page = browser.new_page()

	page.on("response", handle_response)

	page.goto(url, wait_until="networkidle", timeout = 5000)

	page.pause()