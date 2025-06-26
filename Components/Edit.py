import os

from moviepy.editor import VideoFileClip
from moviepy.video.VideoClip import TextClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
from moviepy.video.fx import fadein

from Components.Transcription import transcribe_audio


def extract_audio(video_path, out_path):
    try:
        video_clip = VideoFileClip(video_path)
        if not os.path.exists('audio'):
            os.makedirs('audio')

        audio_path = f"audio/{out_path}"
        video_clip.audio.write_audiofile(audio_path)
        video_clip.close()
        print(f"Extracted audio to: {audio_path}")
        return audio_path
    except Exception as e:
        print(f"An error occurred while extracting audio: {e}")
        return None

def extract_audio_from_video(video, out_path):
    try:
        if not os.path.exists('audio'):
            os.makedirs('audio')

        audio_path = f"audio/{out_path}"
        video.audio.write_audiofile(audio_path)
        video.close()
        print(f"Extracted audio to: {audio_path}")
        return audio_path
    except Exception as e:
        print(f"An error occurred while extracting audio: {e}")
        return None



def crop_video(input_file, output_file, start_time, end_time):
    with VideoFileClip(input_file) as video:
        cropped_video = video.subclip(start_time, end_time)
        cropped_video.write_videofile(output_file, codec='libx264')


def add_captions(input_video, output_video, font="Arial-Bold", fontsize=50, color="white",
                 stroke_color="black", stroke_width=2):
    video = VideoFileClip(input_video)

    audio_short = extract_audio(video, "short.wav")
    captions = transcribe_audio(audio_short, True)

    # Crear una lista para los clips de subtítulos
    subtitle_clips = []

    for start, end, text in captions:
        # Crear un clip de texto para cada subtítulo
        text_clip = (
            TextClip(
                text,
                font=font,
                fontsize=fontsize,
                color=color,
                stroke_color=stroke_color,
                stroke_width=stroke_width,
            )
            .set_position(("center", "bottom"))  # Posición: centro inferior
            .set_start(start)  # Tiempo de inicio del subtítulo
            .set_duration(end - start)  # Duración del subtítulo
        )
        subtitle_clips.append(text_clip)

    # Combinar los subtítulos con el video
    final_video = CompositeVideoClip([video] + subtitle_clips)

    # Exportar el video final con subtítulos
    final_video.write_videofile(output_video, codec="libx264", audio_codec="aac")


def add_karaoke_captions(input_video, output_video, font="Arial-Bold", fontsize=50, base_color="white",
                         highlight_color="green", stroke_color="black", stroke_width=2):
    video = VideoFileClip(input_video)

    # Extract the audio and transcribe it with word-level timestamps
    audio_short = extract_audio_from_video(video, "short.wav")
    captions = transcribe_audio(audio_short, True, word_level=True)  # Ensure this returns word-level timestamps

    # Crear una lista para los clips de subtítulos
    subtitle_clips = []

    for caption in captions:
        start, end, text = caption["start"], caption["end"], caption["text"]
        words = text.split()

        # Dividir la duración entre palabras
        word_duration = (end - start) / len(words)
        word_start = start

        for word in words:
            word_end = word_start + word_duration

            # Clip para palabra no resaltada (base)
            base_word_clip = (
                TextClip(
                    word,
                    font=font,
                    fontsize=fontsize,
                    color=base_color,
                    stroke_color=stroke_color,
                    stroke_width=stroke_width,
                )
                .set_position(("center", "bottom"))
                .set_start(word_start)
                .set_duration(word_duration)
            )

            # Clip para palabra resaltada (karaoke efecto)
            highlight_word_clip = (
                TextClip(
                    word,
                    font=font,
                    fontsize=fontsize,
                    color=highlight_color,
                    stroke_color=stroke_color,
                    stroke_width=stroke_width,
                )
                .set_position(("center", "bottom"))
                .set_start(word_start)
                .set_duration(word_duration)
                .fx(fadein, 0.1)  # Pequeño efecto de aparición
            )

            subtitle_clips.append(base_word_clip)
            subtitle_clips.append(highlight_word_clip)

            # Actualizar el tiempo para la próxima palabra
            word_start = word_end

    # Combinar los clips de subtítulos con el video original
    final_video = CompositeVideoClip([video] + subtitle_clips)

    # Exportar el video final con subtítulos tipo karaoke
    final_video.write_videofile(output_video, codec="libx264", audio_codec="aac")


# Example usage:
if __name__ == "__main__":
    input_file1 = r"Example.mp4"  # Test
    print(input_file1)
    output_file1 = "Short.mp4"
    start_time1 = 31.92
    end_time1 = 49.2

    crop_video(input_file1, output_file1, start_time1, end_time1)
