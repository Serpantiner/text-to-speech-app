from google.cloud import texttospeech
from pydub import AudioSegment
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def split_text_into_chunks(text, max_chunk_size=5000):
    logging.info('Splitting text into chunks')
    words = text.split()
    chunks = []
    current_chunk = ""

    for word in words:
        if len(current_chunk.encode('utf-8')) + len(word.encode('utf-8')) + 1 > max_chunk_size:
            chunks.append(current_chunk)
            current_chunk = word
        else:
            if current_chunk:
                current_chunk += " " + word
            else:
                current_chunk = word

    if current_chunk:
        chunks.append(current_chunk)

    logging.info(f'Text split into {len(chunks)} chunks')
    return chunks

def text_to_speech(text, lang, output_file):
    client = texttospeech.TextToSpeechClient()
    logging.info('Starting text-to-speech conversion')

    def synthesize_speech_chunk(chunk, chunk_index):
        logging.info(f'Synthesizing chunk {chunk_index + 1}/{len(chunks)}')
        input_text = texttospeech.SynthesisInput(text=chunk)
        voice = texttospeech.VoiceSelectionParams(
            language_code=lang,
            name='en-US-Studio-M',
            ssml_gender=texttospeech.SsmlVoiceGender.MALE
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.LINEAR16
        )
        response = client.synthesize_speech(
            input=input_text, voice=voice, audio_config=audio_config
        )
        return response.audio_content

    chunks = split_text_into_chunks(text)
    audio_segments = []

    for i, chunk in enumerate(chunks):
        audio_content = synthesize_speech_chunk(chunk, i)
        temp_chunk_file = f'temp_chunk_{i}.wav'
        with open(temp_chunk_file, 'wb') as out:
            out.write(audio_content)
        audio_segments.append(AudioSegment.from_wav(temp_chunk_file))
        os.remove(temp_chunk_file)

    logging.info('Combining audio segments')
    combined = sum(audio_segments)
    combined.export(output_file, format="wav")
    logging.info(f'Audio content written to file "{output_file}"')