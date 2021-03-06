from __future__ import unicode_literals
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
import shutil

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

def offlineAlterInfoDict():
	global originalRootDir
	originalRootDir = str(Path().absolute()) 

	rootdir = str(Path().absolute()) 
	subfolders = [f.path for f in os.scandir(rootdir + "/") if f.is_dir() ]    

	for subfolderPath in subfolders:
		os.chdir(os.path.join(rootdir, subfolderPath))
		filePath = os.path.join(subfolderPath,'songsInfo.json' )
		with open(filePath, 'r') as fp:
			data = json.load(fp)

		past = data["Original Song Names"]
		removedDupes = list(dict.fromkeys(past))
		if past != removedDupes:
			print(past)
			print(removedDupes)
		data["Original Song Names"] = removedDupes

		with open('songsInfo.json', 'w') as fp:
			json.dump(data, fp, sort_keys=True, indent=4)
	
		

def alterInfoDict():
	#for each song
	rootdir = str(Path().absolute()) 
	subfolders = [f.path for f in os.scandir(rootdir + "/") if f.is_dir() ]    


	for subfolderName in subfolders:
		# delete if mashup is a lot of songs ("AND MORE") else process it
		if " more" in subfolderName.lower() or "top" in subfolderName.lower():
			#TODO delete that folder
			shutil.rmtree(os.path.join(rootdir, subfolderName))

		else:
			#go into that folder
			os.chdir(os.path.join(rootdir, subfolderName))
			#find the original song name
			songName = os.path.basename(subfolderName)
			originalSongNames = list(dict.fromkeys(processSongNames(songName)))

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
			    json.dump(info_dict, fp, sort_keys=True, indent=4)
	


def youtubeSongName(oneSongName):
	"""check on youtube and get the title of the actual song name"""
	ydl_opts = {
		"quiet": True,
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
			try:
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
			except Exception as e:
				print(vid)
			else:
				return "Can't Find Song", []

			
			



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
		"outtmpl": os.path.join(rootdir, "Original_%(title)s.%(ext)s"), #"%(title)s.%(ext)s",
		"ignoreerrors": True, #Do not stop on download errors.
		"nooverwrites": True, #Prevent overwriting files.
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
			shutil.rmtree(os.path.join(rootdir, subfolderName))

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




def test():
	"""Test by processing downloaded sv & downloading original"""
	# processDownloads()
	testCaseProb = "「Nightcore」→  Faded ✗Running With The Wolves (Switching Vocals)"
	testCaseProbB = "「Nightcore」→  Faded _ Running With The Wolves (Switching Vocals)"
	testCaseNorm = "Nightcore ⟿ These Girls [Switching Vocals]"
	testCaseNormB = "Nightcore ⇢ Rockabye (Switching Vocals)"
	testCaseNormC = "❖ Nightcore ❖ ⟿ Come to Brazil [Switching Vocals]"
	testCaseProbC = "Nightcore ⇢ Solo (Switching Vocals) By Halocene" 
	tests = [testCaseProb, testCaseProbB, testCaseNorm, testCaseNormB, testCaseNormC, testCaseProbC]
	correctAns = [str(['Faded', 'Running with the Wolves']), str(['Faded', 'Running with the Wolves']),
	str(["Why Don't We- These Girls (lyrics)"]), 
	str(['Rockabye (feat. Sean Paul & Anne-Marie)']), 
	str(['Come to Brazil']),
	str(['Solo (feat. Demi Lovato)'])
	]
	results = []
	for i in range(len(tests)):
		ans = str(processSongNames(tests[i]))
		results.append(ans)
		print("#")

	print("\n")
	for i in range(len(results)):
		if results[i] == correctAns[i]:
			print("CORRECT :D \n")
		else:
			print("WRONG! \nFor test case: " + tests[i])
			print("Answer produced: " + results[i])
			print("Correct Answer: " + correctAns[i])
			print("\n")
			print("###### VERBOSE #######")
			processSongNamesVerbose(tests[i])
			
	# processSongNames(testCase)
	

def run():
	processDownloads()
	
	
	##### Process
	#put in folder for each song
	#find the original song
	#download the original song and put in the same folder
	#rename to Original and SV




if __name__ == "__main__":
    run()
    # offlineAlterInfoDict()
    # alterInfoDict()
    
    