from __future__ import unicode_literals

import shutil
import youtube_dl
import os
from pathlib import Path
import json
import os
import string
from pathlib import Path
from unidecode import unidecode
import re
from string import punctuation
import youtube_dl

def flatten(A):
	rt = []
	for i in A:
		if isinstance(i,list): rt.extend(flatten(i))
		else: rt.append(i)
	return rt


def nameSplitter(SVName, verbose = False):
	#remove unicode
	# SVName = (SVName.encode('ascii',errors='ignore')).decode()
	if verbose:
		print(SVName)

	SVName = SVName.replace("✗", " _ ")

	if verbose:
		print(SVName)


	SVName = unidecode(SVName) #better coz it brings to the closest equivalent

	if verbose:
		print(SVName)


	#remove punctuation
	# SVName = SVName.translate(str.maketrans('', '', string.punctuation))

	#remove the nightcore & switching vocals part using regex
	regexPhrase = r"(?!Nightcore|Switching Vocals|Vocals|lyrics|Lyrics|MASHUP)(\b[a-zA-Z0-9]+[-,'._ a-zA-Z0-9]*)+(?!Nightcore|Switching Vocals|Vocals|lyrics|Lyrics)"
	possibleNames = re.findall(regexPhrase,SVName)
	# print(SVName)

	#filter out the Switching Vocals & Mashups from the list
	to_remove = ['Mashups', 'Switching Vocals', 'Mashup', "sing off"]

	p = re.compile('|'.join(map(re.escape, to_remove))) # escape to handle metachars
	#filter out extra words
	ConfirmNames = [p.sub('', s) for s in possibleNames]
	#strip trailing punctuation
	ConfirmNames = [s.rstrip(punctuation + " ") for s in ConfirmNames]
	
	#split songs if they are more than one song /// also do something about artists
	songNames = flatten([s.split("_") for s in ConfirmNames])

	songNames = flatten([s.split("-") for s in songNames])

	songNames = [s.strip(punctuation + " ") for s in songNames]

	songNames = [s for s in songNames if len(s) > 0]


	return songNames

def youtubeSongName(oneSongName):
	"""check on youtube and get the title of the actual song name"""
	ydl_opts = {
		# "quiet": True,
		# "outtmpl": "%(title)s.%(ext)s", #file name is song name
		# "outtmpl": os.path.join(rootdir,"%(title)s/SV.%(ext)s"), #folder name is song name, file is SV
		"ignoreerrors": True, #Do not stop on download errors.
		"nooverwrites": True, #Prevent overwriting files.
		"matchtitle": oneSongName, #not sure if this works (Download only matching titles)
		"reject-title": r"(Switching Vocals|Mashups)",		# "writedescription": True, #Write the video description to a .description file
		"skip_download": True, #don't actually download the video
		"min_views": 100, #only get videos with min 10k views
		# "download_archive": "alreadyListedFiles.txt", #File name of a file where all downloads are recorded. Videos already present in the file are not downloaded     again.
		"default_search": "ytsearch: lyrics ", #Prepend this string if an input url is not valid. 'auto' for elaborate guessing'
		'format': 'bestaudio/best',
		'postprocessors': [{
			'key': 'FFmpegExtractAudio',
			'preferredcodec': 'wav',
			'preferredquality': '192'
		}],
		'postprocessor_args': [
		'-ar', '16000'
		],
		'prefer_ffmpeg': True,
		'keepvideo': True
		}
	with youtube_dl.YoutubeDL(ydl_opts) as ydl:
		ydl.add_default_info_extractors()
		# ydl.download(oneSongName)
		info_dict = ydl.extract_info(oneSongName, download=False)
		# print(info_dict) 
		if info_dict == None:
			return "Can't Find Song", []

		#check if there are any entires
		vid = info_dict["entries"]
		if vid == None or len(vid) == 0:
			return "Can't Find Song", []
		else:
			video = vid[0]
			# print("#############")
			# print(video)
			# print("#############")
			# we get back a playlist object so access title as below (alt_title sees to work better)
			title = video.get("alt_title")

			if title == None or len(title) < 1:
				title = video.get("title")

			if title == None or len(title) < 1:
				return "Can't Find Song", []
			#list of terms that should be removed from snippets list coz same song
			otherPossibleNames = []

			listOfImportantTerms = [
			"creator",
			"title",
			"alt_title",
			"track",
			"artist", 
			"album",
			"tags"
			] #TODO
			for i in listOfImportantTerms:
				item = video.get(i)
				if item != None and len(item) > 0: #remove blanks
					otherPossibleNames.append(item)


			#flatten list 
			otherPossibleNames = flatten(otherPossibleNames)

			#make everything lower case
			otherPossibleNames = [s.lower() for s in otherPossibleNames]
			return title, otherPossibleNames



def properSongNames(listOfPossibleSongs):
	"""check for duplicate song and song vs artist dups & get proper name API"""
	## get proper name #TODO if got artist name and song name separate...
	# songNames = [youtubeSongName(s) for s in listOfPossibleSongs]

	#TODO don't process snippets from listOfPossibleSongs if it matches entry in already Marked
	alreadyFoundTerms = []
	songNamesList = []


	# first send the entire snippet through (in case it is just one song)
	if len(listOfPossibleSongs) > 1:
		fullListQuery = " ".join(listOfPossibleSongs)
		listOfPossibleSongs.insert(0, fullListQuery)

	for i in listOfPossibleSongs:
		#if snippet is in alreadyFoundTerms, ignore it
		if i.lower() in alreadyFoundTerms:
			pass
		else:
			title, newTerms = youtubeSongName(i)
			songNamesList.append(title)
			alreadyFoundTerms.extend(alreadyFoundTerms)

	return songNamesList


	# return songNamesList


	## remove dupes
	songNames = list(dict.fromkeys(songNamesList))

	## remove empties
	songNames = [s for s in songNames if len(s) > 0]


	return songNames


# print(rootdir)

def DownloadASong(SongName):
	""" Get the list of results from queries and put it in a json file"""
	rootdir = str(Path().absolute())
	ydl_opts = {
		"quiet": True,
		"outtmpl": os.path.join(rootdir, "Original_%(title)s.%(ext)s"), #"%(title)s.%(ext)s",
		"ignoreerrors": True, #Do not stop on download errors.
		"nooverwrites": False, #Prevent overwriting files.
		"writedescription": True, #Write the video description to a .description file
		"min_views": 100, #only get videos with min 10k views
		# "download_archive": "alreadyListedFiles.txt", #File name of a file where all downloads are recorded. Videos already present in the file are not downloaded     again.
		"default_search": "auto", #Prepend this string if an input url is not valid. 'auto' for elaborate guessing'
		'format': 'bestaudio/best',
	    'postprocessors': [{
	        'key': 'FFmpegExtractAudio',
	        'preferredcodec': 'wav',
	        'preferredquality': '192'
	    }],
	    'postprocessor_args': [
	        '-ar', '16000'
	    ],
	    'prefer_ffmpeg': True,
	    'keepvideo': True
		}
	with youtube_dl.YoutubeDL(ydl_opts) as ydl:
	    ydl.download([SongName])

def processSongNamesVerbose(songName):
	# songName = os.path.basename(subfolderName)
	# print(songName)
	# print(os.listdir())
	splitNames = nameSplitter(songName, True)
	songTitles = properSongNames(splitNames)
	#remove the can't find songs
	properTitles = [s for s in songTitles if s != "Can't Find Song"]

	print("###########/////Checking///////#############")
	print(songName)
	print(splitNames)
	print(songTitles)

	return properTitles

def processSongNames(songName):
	# songName = os.path.basename(subfolderName)
	# print(songName)
	# print(os.listdir())
	splitNames = nameSplitter(songName)
	songTitles = properSongNames(splitNames)
	#remove the can't find songs
	properTitles = [s for s in songTitles if s != "Can't Find Song"]

	# print("###########/////Checking///////#############")
	# print(songName)
	# print(splitNames)
	# print(songTitles)

	return properTitles




def processDownloads():
	"""repeatedly sorts downloaded vid into it's folder and downloads the original into the same folder"""
	##### Process
	#for each song
	rootdir = str(Path().absolute()) 
	subfolders = [f.path for f in os.scandir(rootdir + "/") if f.is_dir() ]    


	for subfolderName in subfolders:
		# delete if mashup is a lot of songs ("AND MORE") else process it
		if "and more" in subfolderName.lower():
			#TODO delete that folder
			os.removedirs(os.path.join(rootdir, subfolderName))

		else:
			#go into that folder
			os.chdir(os.path.join(rootdir, subfolderName))
			#find the original song name
			songName = os.path.basename(subfolderName)
			originalSongNames = processSongNames(songName)

			#TODO save the name of the song to a file in the folder ALONG with SV name
			mashupVid = False
			if len(originalSongNames) > 1 or "mashup" in songName.lower():
				mashupVid = True

			PossibleError = False
			if "mashup" in songName.lower() and len(originalSongNames) < 2:
				print("Error: possibly missing song for " + songName)
				PossibleError = True

			info_dict = {
			"Switch Vocals Vid": songName,
			"Original Song Names": originalSongNames,
			"Mashup": mashupVid,
			"Error(if MashUp)": PossibleError
			}

			with open('songsInfo.json', 'w') as fp:
			    # json.dump(data, fp)
			    json.dump(info_dict, fp, sort_keys=True, indent=4)
			#TODO download the original song and put in the same folder
			for i in originalSongNames:
				DownloadASong(i) #TODO verify this is in correct folder
			#rename to Originals and SV (kinda already done - orignals have appended titles coz)

def writeToErrorFile(message):
	global originalRootDir
	myPath = os.path.join(originalRootDir + "Error_Verify.txt")
	text_file = open(myPath, "w")
	n = text_file.write(message)
	text_file.close()
	return

def writeToWarningFile(message):
	global originalRootDir
	myPath = os.path.join(originalRootDir + "Warning_Verify.txt")
	text_file = open(myPath, "w")
	n = text_file.write(message)
	text_file.close()
	return



def countOriginals(subfolderPath):
	"""return count of original vids"""
	items = os.listdir(subfolderPath)
	count = 0
	for file in items:
		if file.startswith("Original_") and file.endswith(".description"):
			count = count + 1
	return count

def checkMissingSongs(subfolderPath):
	filePath = os.path.join(subfolderPath,'songsInfo.json' )
	with open(filePath, 'r') as fp:
		data = json.load(fp)
	#check number of original songs
	countOriginalsDownloaded = countOriginals(subfolderPath)

	if len(data["Original Song Names"]) != countOriginalsDownloaded:
		if len(data["Original Song Names"]) > countOriginalsDownloaded:
			print("Missing Songs! for " + data["Switch Vocals Vid"])
			return 2
		else:
			#too many original songs downloaded
			print("###### Possible Error ####### Too many originals for: " + data["Switch Vocals Vid"])
			return 1
	else:
		return 0

def whichSongsAreMissing(subfolderPath):
	"""returns query names of missing songs"""
	filePath = os.path.join(subfolderPath,'songsInfo.json' )
	with open(filePath, 'r') as fp:
		data = json.load(fp)
	items = os.listdir(subfolderPath)
	allSongNames = data["Original Song Names"]
	included = []
	for file in items:
		if file.startswith("Original_") and file.endswith(".description"):
			fileName = os.path.basename(file)
			songName = fileName[9:-12]
			# print(songName)
			# name, terms = youtubeSongName(songName)
			included.append(songName)
			# print(included)
			# flatten(included)
	missingSongs = list(set(allSongNames)^set(included))
	return missingSongs

def FixMissingDownloads():
	"""check if folder has correct number of originals"""
	##### Process
	#for each song
	global originalRootDir
	originalRootDir = str(Path().absolute()) 

	rootdir = str(Path().absolute()) 
	subfolders = [f.path for f in os.scandir(rootdir + "/") if f.is_dir() ]    

	for subfolderName in subfolders:
		# go into that folder
		# os.chdir(subfolderName)
		#find the originals needed from info json
		problem = checkMissingSongs(subfolderName)
		if(problem != 0):
			#something is wrong
			if problem == 1:
				#too many originals
				writeToErrorFile("Too Many Songs: " + str(subfolderName))
				#move to problematicSongVid
				shutil.move(subfolderName, "/Users/Caffae/Documents/GitHub/SwitchingVocalsNN/Problematic_SongVids/TooMany")
				problem = 0 # to break out

			if problem == 2:
				#too little originals
				missingSongs = whichSongsAreMissing(subfolderName)
				for SongName in missingSongs:
					DownloadASong(SongName)
				problem = checkMissingSongs(subfolderName)

		if problem != 0:
			#too little originals cannot be downloaded
			writeToErrorFile("Too little songs (download problem): " + str(subfolderName))
			#move to problematicSongVid
			dest = "/Users/Caffae/Documents/GitHub/SwitchingVocalsNN/Problematic_SongVids/TooLittle(DownloadProb)"
			shutil.move(subfolderName, dest)
	return 


def removeFoldersWithNoOriginals():
	global originalRootDir
	originalRootDir = str(Path().absolute()) 

	rootdir = str(Path().absolute()) 
	subfolders = [f.path for f in os.scandir(rootdir + "/") if f.is_dir() ]    

	for subfolderName in subfolders:
		if countOriginals(subfolderName) == 0:
			writeToErrorFile("No downloaded original : " + str(subfolderName))
			dest = "/Users/Caffae/Documents/GitHub/SwitchingVocalsNN/Problematic_SongVids/No_Originals"
			shutil.move(subfolderName, dest)
	return

# import librosa
from pydub import AudioSegment
def possiblyTooLong():
	global originalRootDir
	originalRootDir = str(Path().absolute()) 

	rootdir = str(Path().absolute()) 
	subfolders = [f.path for f in os.scandir(rootdir + "/") if f.is_dir() ]    

	for subfolderName in subfolders:
		allFiles = os.listdir(subfolderName)
		for file in allFiles:
			if file.endswith(".wav"):
				#check if song is too long
				# songLength = librosa.get_duration(file)
				audioFilePath = os.path.abspath(os.path.join(rootdir, subfolderName, file))
				audio = AudioSegment.from_file(audioFilePath)
				songLength = audio.duration_seconds
				# print(songLength)
				if songLength > 500 or songLength < 120:
					writeToWarningFile("Song Might be too long : " + str(subfolderName))
					dest = "/Users/Caffae/Documents/GitHub/SwitchingVocalsNN/Problematic_SongVids/WrongSong"
					shutil.move(subfolderName, dest)
					break;
	return 
		

def run():
	FixMissingDownloads()
	# print("Done")
	removeFoldersWithNoOriginals()
	# print("Done")
	possiblyTooLong()
	# print("Done")
	#TODO test for similarity of song
	
	##### Process
	#put in folder for each song
	#find the original song
	#download the original song and put in the same folder
	#rename to Original and SV




if __name__ == "__main__":
    run()
    