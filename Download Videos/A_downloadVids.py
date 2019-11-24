from __future__ import unicode_literals
import youtube_dl
import os
from pathlib import Path


def QueryYoutube(QueryList, toSkip = True):
	rootdir = str(Path().absolute())
	""" Get the list of results from queries and put it in a json file"""
	ydl_opts = {
		# "outtmpl": "%(title)s.%(ext)s", #file name is song name
		"outtmpl": os.path.join(rootdir,"%(title)s/SV.%(ext)s"), #folder name is song name, file is SV
		"ignoreerrors": True, #Do not stop on download errors.
		"nooverwrites": True, #Prevent overwriting files.
		"matchtitle": "Switching Vocals", #not sure if this works (Download only matching titles) substring is caseless
		"reject-title": r"([0-9]{4}|Top|[mM][eE][gG][aA][ ]*[mM][iI][xX]|and MORE|DECADE|Songs of|[0-9] [Hh][Oo][Uu][Rr]| Special|The Greatest|Medley|[ONEoneTWtwHRhrFfUuRrIiVvEe ]{0,6}[Hh][Oo][Uu][Rr]|[0-9]{0,3}\+)",
		"writedescription": True, #Write the video description to a .description file
		"skip_download": toSkip, #don't actually download the video
		"min_views": 100, #only get videos with min 10k views
		"download_archive": "alreadyListedFiles.txt", #File name of a file where all downloads are recorded. Videos already present in the file are not downloaded     again.
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
	    ydl.download(QueryList)


def test():
	"""Test by downloading two sets of two SV"""
	# queriesL = ["nightcore mashups", "bts mashups", "ytuser:https://www.youtube.com/channel/UC5XWNylwy4efFufjMYqcglw"]
	# queriesL = ["ytuser:https://www.youtube.com/channel/UC5XWNylwy4efFufjMYqcglw", "ytuser:"]

	#nightcore switching vocals
	queriesL = [ 
	# "https://www.youtube.com/channel/UCPMhsGX1A6aPmpFPRWJUkag", 
				# "https://www.youtube.com/channel/UCl2fdq_CzdrDhauV85aXQDQ",
				# "https://www.youtube.com/channel/UC8Y2KrSAhAl1-1hqBGLBdzA",
				# "https://www.youtube.com/channel/UCJsX7vcaCUdPOcooysql1Uw",
				# "https://www.youtube.com/channel/UCtY3IhWM6UOlMBoUG-cNQyQ",
				"https://www.youtube.com/channel/UCNOymlVIxfFW0mVmZiNq6DA"
				]
	# QueryYoutube(queriesL, True) #should download that channel
	QueryYoutube(queriesL, False) #should download that channel

def run():
	##### DOWNLOADING
	#nightcore switching vocals channels
	queriesL = ["https://www.youtube.com/channel/UCPtWGnX3cr6fLLB1AAohynw", 
				"https://www.youtube.com/channel/UCPMhsGX1A6aPmpFPRWJUkag", 
				"https://www.youtube.com/channel/UCl2fdq_CzdrDhauV85aXQDQ",
				"https://www.youtube.com/channel/UC8Y2KrSAhAl1-1hqBGLBdzA",
				"https://www.youtube.com/channel/UCJsX7vcaCUdPOcooysql1Uw",
				"https://www.youtube.com/channel/UCtY3IhWM6UOlMBoUG-cNQyQ",
				"https://www.youtube.com/channel/UCNOymlVIxfFW0mVmZiNq6DA"
				]
	QueryYoutube(queriesL, False)

	##### Process
	#put in folder for each song
	#find the original song
	#download the original song and put in the same folder
	#rename to Original and SV

def downloadChannels(queriesL):
	QueryYoutube(queriesL, False)



if __name__ == "__main__":
    run()
    