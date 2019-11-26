from musicnn.extractor import extractor
from musicnn.tagger import top_tags
import numpy as np
import matplotlib.pyplot as plt
import os
import json
from pathlib import Path

def plotOutDiagrams(songPath, modelUsed, subfolderName = False, show = False):
	# print("The Path is " + songPath)
	taggram, tags, somethingElse = extractor(songPath, model=modelUsed)

	
	if "SV.wav" == songPath and subfolderName:
		# songName = "SV_" + os.path.basename(os.path.dirname(songPath))
		# print("SubfolderName: " + subfolderName)
		# print("DirName: " + os.path.dirname(subfolderName))
		# print("BaseName: " + os.path.basename(subfolderName))
		songName = "SV_" + os.path.basename(subfolderName)
	else:
		songName = os.path.basename(songPath)[:-4]

	# print("The song name is " + songName)

	in_length = 3 # seconds  by default, the model takes inputs of 3 seconds with no overlap

	plt.rcParams["figure.figsize"] = (10,8) # set size of the figures
	fontsize = 12 # set figures font size

	fig, ax = plt.subplots()


	# title
	ax.title.set_text('Taggram ' + songName + " " + modelUsed)
	ax.title.set_fontsize(fontsize)

	# x-axis title
	ax.set_xlabel('(seconds)', fontsize=fontsize)

	# y-axis
	y_pos = np.arange(len(tags))
	ax.set_yticks(y_pos)
	ax.set_yticklabels(tags, fontsize=fontsize-1)

	# x-axis
	x_pos = np.arange(taggram.shape[0])
	x_label = np.arange(in_length/2, in_length*taggram.shape[0], 3)
	ax.set_xticks(x_pos)
	ax.set_xticklabels(x_label, fontsize=fontsize)

	# depict taggram
	ax.imshow(taggram.T, interpolation=None, aspect="auto")
	if show:
		plt.show()

	plt.savefig("Taggram " + songName + " _ " + modelUsed + ".png")


	####

	tags_likelihood_mean = np.mean(taggram, axis=0) # averaging the Taggram through time

	fig, ax = plt.subplots()

	# title
	ax.title.set_text('Tags likelihood (mean of the taggram) ' + songName)
	ax.title.set_fontsize(fontsize)

	# y-axis title
	ax.set_ylabel('(likelihood)', fontsize=fontsize)

	# y-axis
	ax.set_ylim((0, 1))
	ax.tick_params(axis="y", labelsize=fontsize)

	# x-axis
	ax.tick_params(axis="x", labelsize=fontsize-1)
	pos = np.arange(len(tags))
	ax.set_xticks(pos)
	ax.set_xticklabels(tags, rotation=90)

	# depict song-level tags likelihood
	ax.bar(pos, tags_likelihood_mean)

	if show:
		plt.show()
	# plt.show()
	plt.savefig("Tags likelihood " + songName + " " + modelUsed + ".png")
	plt.close('all')

	return taggram, tags

def TagsDiagram(tags, songPath):
	if "SV.wav" in songPath:
		songName = "SV_" + os.path.basename(os.path.dirname(songPath))
	else:
		songName = os.path.basename(songPath)[:-4]

	global modelUsed

	tags_likelihood_mean = np.mean(taggram, axis=0) # averaging the Taggram through time

	fig, ax = plt.subplots()

	# title
	ax.title.set_text(songName + " " + modelUsed)
	ax.title.set_fontsize(fontsize)

	# y-axis title
	ax.set_ylabel('(likelihood)', fontsize=fontsize)

	# y-axis
	ax.set_ylim((0, 1))
	ax.tick_params(axis="y", labelsize=fontsize)

	# x-axis
	ax.tick_params(axis="x", labelsize=fontsize-1)
	pos = np.arange(len(tags))
	ax.set_xticks(pos)
	ax.set_xticklabels(tags, rotation=90)

	# depict song-level tags likelihood
	ax.bar(pos, tags_likelihood_mean)

	return plt

def TaggramDiagram(taggram, tags, songPath):
	if "SV.wav" in songPath:
		songName = "SV_" + os.path.basename(os.path.dirname(songPath))
	else:
		songName = os.path.basename(songPath)[:-4]
	global modelUsed
	in_length = 3 # seconds  by default, the model takes inputs of 3 seconds with no overlap
	# plt.rcParams["figure.figsize"] = (10,8) # set size of the figures
	fontsize = 12 # set figures font size
	fig, ax = plt.subplots()

	# title
	ax.title.set_text(songName + " " + modelUsed)
	ax.title.set_fontsize(fontsize)

	# x-axis title
	ax.set_xlabel('(seconds)', fontsize=fontsize)

	# y-axis
	y_pos = np.arange(len(tags))
	ax.set_yticks(y_pos)
	ax.set_yticklabels(tags, fontsize=fontsize-1)

	# x-axis
	x_pos = np.arange(taggram.shape[0])
	x_label = np.arange(in_length/2, in_length*taggram.shape[0], 3)
	ax.set_xticks(x_pos)
	ax.set_xticklabels(x_label, fontsize=fontsize)

	# depict taggram
	ax.imshow(taggram.T, interpolation=None, aspect="auto")
	# if show:
	# 	plt.show()

	# plt.savefig("Taggram " + songName + ".png")
	return plt

def plotSeveralDiagrams(taggram, tags, diagramType, songPathL):
	numberOfPoints = len(listOfInfo)
	if numberOfPoints % 2 == 0:
		w = int(numberOfPoints/2)
		h = 2
	elif numberOfPoints % 3 == 0:
		w = int(numberOfPoints/3)
		h = 3
	elif numberOfPoints % 5 == 0:
		w = int(numberOfPoints/5)
		h = 5
	else: 
		w = 10
		h = 10
		print("Max 100 diagrams")

	if w < 1:
		w = 1

	fig, axs = plt.subplots(h,w, figsize=(15, 6), sharex=True, sharey=True)
	count = 0
	for row in range(h):
		for column in range(w):
			if diagramType == "Taggram":
				axs[row,column] = TaggramDiagram(taggram[count], tags[count], songPathL[count])
				count = count + 1
			elif diagramType == "Tags":
				axs[row,column] = TagsDiagram(tags[count], songPathL[count])
				count = count + 1
			else:
				print("Error")

	# for i, ax in enumerate(axes.flatten()):
 #    ax.bar(x, y[:,i], color=plt.cm.Paired(i/10.))

	plt.show()
	plt.savefig(modelUsed + " " + diagramType + ".png")

	

def MultipleSongs(songList, modelUsed):
	taggramL = []
	tagsL = []
	for i in songList:
		taggrams, tags = plotOutDiagrams(i, modelUsed)
		taggramL.append(taggrams)
		tagsL.append(tags)

	plotSeveralDiagrams(taggramL, tagsL, "Taggram", songList)
	plotSeveralDiagrams(taggramL, tagsL, "Tags", songList)

def ProcessAll(modelUsed):
	# global modelUsed
	# modelUsed = modelToUse

	rootdir = str(Path().absolute()) 
	subfolders = [f.path for f in os.scandir(rootdir + "/") if f.is_dir() ]    
	for subfolderName in subfolders:
		currentDirectory = os.path.join(rootdir, subfolderName)
		os.chdir(currentDirectory)
		#find the original song name
		songName = os.path.basename(subfolderName)
		print("Working At: " + songName)
		items = os.listdir(currentDirectory)
		for file in items:
			if file.endswith(".wav"):
				taggrams, tags = plotOutDiagrams(file, modelUsed, currentDirectory)
				# matplotlib.close('all')
				info_dict = {
				"taggrams" : taggrams, 
				"tags" : tags
				}

				if "SV.wav" == file:
					songName = "SV_" + os.path.basename(currentDirectory)
				else:
					songName = os.path.basename(file)[:-4]
				jsonName = songName + ".json"
				with open(jsonName, 'w') as fp:
				    # json.dump(data, fp)
				    json.dump(info_dict, fp, sort_keys=True, indent=4)


		print("Done with " + songName)

def test():
	# global modelUsed
	modelUsed = "MTT_musicnn" # modelUsed = "MSD_musicnn"
	songPathOrig = "/Users/Caffae/Documents/GitHub/SwitchingVocalsNN/SongVids/「Nightcore」→ Love Yourself ( Switching Vocals )/Original_Justin Bieber - Love Yourself (Official Video).wav"
	songPathSV = "/Users/Caffae/Documents/GitHub/SwitchingVocalsNN/SongVids/「Nightcore」→ Love Yourself ( Switching Vocals )/SV.wav"
	# songPathNewOrig = "/Users/Caffae/Documents/GitHub/SwitchingVocalsNN/SongVids/❖ Nightcore ❖ ⟿ Think About Us [Switching Vocals _ Little Mix]/Original_Little Mix - Think About Us (Official Video) ft. Ty Dolla $ign.wav"
	# songPathNewSV = "/Users/Caffae/Documents/GitHub/SwitchingVocalsNN/SongVids/❖ Nightcore ❖ ⟿ Think About Us [Switching Vocals _ Little Mix]/SV.wav"
	songPathNewOrig = "/Users/Caffae/Documents/GitHub/SwitchingVocalsNN/SongVids/Nightcore _ Maps (Switching Vocals)/Original_Maroon 5 - Maps (Lyric Video).wav"
	songPathNewSV = "/Users/Caffae/Documents/GitHub/SwitchingVocalsNN/SongVids/Nightcore _ Maps (Switching Vocals)/SV.wav"
	songList = [songPathOrig, songPathSV, songPathNewOrig, songPathNewSV]
	MultipleSongs(songList, modelUsed)

def run():
	ProcessAll("MTT_musicnn")
	ProcessAll("MSD_musicnn")
	



if __name__ == "__main__":
    run()
