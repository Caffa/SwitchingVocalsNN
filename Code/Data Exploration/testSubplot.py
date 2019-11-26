from musicnn.extractor import extractor
from musicnn.tagger import top_tags
import numpy as np
import matplotlib.pyplot as plt
import os


def makeSubPlot(a,b):
	fig, ax = plt.subplots()
	ax.plot(a, b)
	return plt


def run():
	h = 2
	w = 2
	fig, axs = plt.subplots(h,w, figsize=(15, 6), sharex=True, sharey=True)
	count = 0

	listOfInfo = [1,2,3,4]
	songPathL = [1,2,3,4]

	for row in range(h):
		for column in range(w):
			axs[row,column] = makeSubPlot(listOfInfo[count], songPathL[count])
			count = count + 1

	plt.show()



if __name__ == "__main__":
    run()