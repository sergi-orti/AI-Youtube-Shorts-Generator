import glob
import os
import time

from Components.YoutubeDownloader import download_youtube_video
from Components.Edit import extract_audio, crop_video, add_captions, add_karaoke_captions
from Components.Transcription import transcribe_audio
from Components.LanguageTasks import getHighlight
from Components.FaceCrop import crop_to_vertical, combine_videos


def get_shorts():
    url = input("Enter YouTube video URL: ")
    video= download_youtube_video(url)
    if video:
        video = video.replace(".webm", ".mp4")
        print(f"Downloaded video and audio files successfully! at {video}")

        audio = extract_audio(video, "audio.wav")
        if audio:

            transcriptions = transcribe_audio(audio)
            if len(transcriptions) > 0:
                TransText = ""

                for text, start, end in transcriptions:
                    TransText += f"{start} - {end}: {text} \n"

                time_segments = getHighlight(TransText)
                for start, stop, content in time_segments:
                    if start != 0 and stop != 0 or stop-start > 10:
                        if not os.path.exists('results'):
                            os.makedirs('results')

                        video_name = "_".join(content.split()[:5])
                        video_name = "".join(c for c in video_name if c.isalnum() or c == "_")

                        print(f"Start: {start} , End: {stop}")
                        Output = f"results/Out_{video_name}.mp4"

                        crop_video(video, Output, start, stop)
                        cropped = f"results/cropped_{video_name}.mp4"

                        crop_to_vertical(Output, cropped)
                        combined_output = f"results/combined_{video_name}.mp4"
                        combine_videos(Output, cropped, combined_output)

                        final_output = f"results/Final_{video_name}.mp4"
                        add_karaoke_captions(combined_output, final_output)
                        time.sleep(10)

                else:
                    print("Error in getting highlight")
                time.sleep(10)

            else:
                print("No transcriptions found")
        else:
            print("No audio file found")
    else:
        print("Unable to Download the video")

    if os.path.exists("results"):
        out_videos = glob.glob(os.path.join("results", "Out*"))
        cropped_videos = glob.glob(os.path.join("results", "cropped*"))
        combined_videos = glob.glob(os.path.join("results", "combined*"))

        for video in out_videos + cropped_videos + combined_videos:
            try:
                os.remove(video)
                print(f"Deleted: {video}")
            except Exception as e:
                print(f"Error deleting {video}: {e}")

        os.remove(f"audio/audio.wav")

if __name__ == "__main__":
    get_shorts()