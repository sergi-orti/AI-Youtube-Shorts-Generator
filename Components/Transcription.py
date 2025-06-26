from faster_whisper import WhisperModel, tokenizer
import torch


def transcribe_audio(audio_path, return_as_tuples=False, word_level=False):
    try:
        print("Transcribing audio...")
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(device)
        model = WhisperModel("base", device="cuda" if torch.cuda.is_available() else "cpu")  # base.en for english
        print("Model loaded")
        segments, info = model.transcribe(audio=audio_path,
                                          beam_size=5,
                                          language="es",  # language="en"
                                          max_new_tokens=128,
                                          condition_on_previous_text=False)
        segments = list(segments)

        if word_level:
            # Initialize tokenizer to decode tokens into text
            tokenizer = model.hf_tokenizer

            # Process word-level timestamps
            word_transcriptions = []
            for segment in segments:
                segment_duration = segment.end - segment.start
                num_tokens = len(segment.tokens)

                # Divide the segment duration across the number of tokens (words)
                token_duration = segment_duration / num_tokens if num_tokens > 0 else 0

                for i, token in enumerate(segment.tokens):
                    word_start = segment.start + i * token_duration
                    word_end = word_start + token_duration

                    # Decode the token into the actual text
                    word_text = tokenizer.decode([token]).strip()

                    # Append each word with its start and end times
                    word_transcriptions.append({
                        "text": word_text,
                        "start": word_start,
                        "end": word_end
                    })

            return word_transcriptions

        extracted_texts = [[segment.text, segment.start, segment.end] for segment in segments]

        # Convert to tuples if needed
        if return_as_tuples:
            return [(segment.start, segment.end, segment.text) for segment in segments]

        return extracted_texts
    except Exception as e:
        print("Transcription Error:", e)
        return []


if __name__ == "__main__":
    audio_path1 = "audio.wav"
    transcriptions = transcribe_audio(audio_path1)
    print("Done")
    TransText = ""

    for text, start, end in transcriptions:
        TransText += f"{start} - {end}: {text}"
    print(TransText)
