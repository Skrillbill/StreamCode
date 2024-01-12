from youtube_transcript_api import YouTubeTranscriptApi as yt
from youtube_transcript_api.formatters import  TextFormatter, JSONFormatter
from pytube import YouTube, Playlist
from time import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
from datetime import datetime, timedelta

#put link to playlist here
p = Playlist("")
formatter = JSONFormatter()
file_contents = [] #LIST to store the file contents in that gets dumped to the output file later


start = time()

def get_transcripts(video):
    id = video.video_id
    try:
        transcript = formatter.format_transcript(yt.get_transcript(id), indent=2)
        parser = json.loads(transcript)
        file_contents.append("BEGIN VIDEO: " + video.watch_url + "\n")
        for line in parser:
            parsed = str(id) + " : " + str(timedelta(seconds=line["start"])) + ": " + str(line["text"] + "\n")
            file_contents.append(parsed)

        file_contents.append("END VIDEO SCRIPT \n")
        result = ""

    except:
        result = "Subtitles disabled for " + id + "\n"
        file_contents.append(result)

    return result

processes = []
#change max_workers to whatever you want. more = faster
with ThreadPoolExecutor(max_workers=24) as executor:
    for v in p.videos:
        processes.append(executor.submit(get_transcripts, v))

with open('playlist_transcripts.json', 'a', encoding='utf-8') as txt_file:
    txt_file.write('\n'.join([str(content) for content in file_contents]))
    txt_file.close()

#comment this out if you don't want to see any output when its done running
print(f'Time taken: {time() - start}')