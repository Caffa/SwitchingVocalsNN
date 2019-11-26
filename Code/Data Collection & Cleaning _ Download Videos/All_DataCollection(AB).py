import A_downloadVids
import B_processDownloads
import C_FixMissedDownloads


def run():
	channelList = [
	"https://www.youtube.com/channel/UC_OTXxqZn1F0vtqiCLRDEmQ", #ღ NightcoreGalaxy ღ
	"https://www.youtube.com/channel/UCtY3IhWM6UOlMBoUG-cNQyQ", #Foxy
	"https://www.youtube.com/channel/UCNOymlVIxfFW0mVmZiNq6DA", #S A R C A S T I C .
	"https://www.youtube.com/channel/UCgf41dj34t-zhBD9L2WPwyQ", #Cordelia Nightcore
	"https://www.youtube.com/channel/UCjlKUwbB8RXqK1vKOqWxiHg", #Smokey
	"https://www.youtube.com/channel/UCnwu06NdREQjWprJC8fvRWw", #Tommy
	"https://www.youtube.com/channel/UCPtWGnX3cr6fLLB1AAohynw", #Mirima
	"https://www.youtube.com/channel/UCPMhsGX1A6aPmpFPRWJUkag", #Sinon
	"https://www.youtube.com/channel/UCo4c1M2_6IlWjsGy4m_3GSQ", #Nightcore Zodiac
	"https://www.youtube.com/channel/UCdu0ncYJ0MZGl4bnNqi7_oQ" #Bunny-Chan

	]
	A_downloadVids.downloadChannels(channelList)
	B_processDownloads.processDownloads()

	C_FixMissedDownloads.FixMissingDownloads()
	C_FixMissedDownloads.removeFoldersWithNoOriginals()
	C_FixMissedDownloads.possiblyTooLong()


if __name__ == "__main__":
    run()