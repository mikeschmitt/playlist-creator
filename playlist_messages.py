#!/usr/bin/env python
# -*- coding: utf-8 -*- 
import urllib, json, sys

class Song:
	def __init__(self, song_name, web_string, parent = None):
		self.song_name = song_name
		self.web_string = web_string
		self.parent = parent
		
		if parent is None:
			self.path_cost = len(song_name.split())
			self.removal_string = song_name
		else:
			self.path_cost = parent.path_cost + len(song_name.split())
			self.removal_string = " ".join([parent.removal_string, song_name])

	def is_root(self):
		'''Indicate whether Song name is beginning phrase of search string.'''
		return self.parent is None
	
	def get_path(self):
		'''Returns a list of Song objects from current to parent.'''
		path = []
		current_song = self
        
		while not current_song.is_root():
			path.append(current_song)
			current_song = current_song.parent

		path.append(current_song)
		return path

	def print_pretty(self):
		print "Song: {0}, Web String = {1}, Path Cost = {2}".format(self.song_name, self.web_string, self.path_cost)

class Playlist:
	def __init__(self, search_string):
		self.non_result_strings = set()
		self.goal_state = search_string.upper().strip()
		self.search_string = " ".join(search_string.split()).upper()
		
	def get_playlist_web_addresses(self):
		'''Returns web address list of songs on playlist for sent search string.'''
		song_list = []
		end_song = self.depth_first_search(self.search_string)
		
		if end_song is not None:
			for s in reversed(end_song.get_path()):
				song_list.append(s)
		
		return song_list
		#POSSIBLE TO RETRY IF NO RESULTS.  IMPLEMENT FURTHER LOOPS FOR PARTIAL MATCHES IF WANTED
		
	def get_spotify_song(self, current_search, parent = None):
		'''Returns exact match for search string if exists.'''
		current_search = current_search.upper().strip()
		
		if current_search in self.non_result_strings:
			return None
		
		jsonurl = urllib.urlopen("http://ws.spotify.com/search/1/track.json?q=" + current_search)
		dat = json.loads(jsonurl.read())
		
		if dat["info"]["num_results"] == 0:
			self.non_result_strings.add(current_search)
			return None
		else:
			# Assume match within 30 results.
			for i in range(min(30, len(dat["tracks"]))):
				if current_search == dat["tracks"][i]["name"].upper().strip():
					return Song(dat["tracks"][i]["name"], dat["tracks"][i]["href"].replace("spotify:track:", "http://open.spotify.com/track/"), parent)
		
			self.non_result_strings.add(current_search)
			return None
	
	def gen_next_children(self, current_search, parent = None):
		'''Returns next song possibilities for search.'''
		current_search = current_search.upper().split(' ')
		return_list = []
		
		while len(current_search) > 0:
			song = self.get_spotify_song(" ".join(current_search), parent)
			
			if song is not None:
				if song.removal_string.upper().strip() == self.goal_state.upper().strip():
					return [song]
					
				return_list.append(song)
				
			current_search.pop()
		
		return return_list

	def depth_first_search(self, current_search):
		'''Depth first search of songs contained in search string.'''
		dfs_stack = self.gen_next_children(current_search)
		
		while len(dfs_stack) > 0:
			if dfs_stack[0].removal_string.upper().strip() == self.goal_state.upper().strip():
				return dfs_stack[0]
			
			current_song = dfs_stack[0]
			dfs_stack.pop(0)
			dfs_stack = self.gen_next_children(current_search.replace(current_song.removal_string.upper(), ""), current_song) + dfs_stack
			
		return None

### MAIN ###
data = sys.stdin.readline()
p = Playlist(data)
song_list = p.get_playlist_web_addresses()

if song_list is None:
	sys.stdout.write("Unable to generate playlist with given input.")
else:
	for s in song_list:
		sys.stdout.write(s.web_string + "\n")