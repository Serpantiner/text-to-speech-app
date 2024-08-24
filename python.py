import os
import logging
from google.cloud import texttospeech
import PyPDF2
from pydub import AudioSegment

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def read_pdf(file_path):
    """
    Function to read text from a PDF file.
    :param file_path: Path to the PDF file.
    :return: Extracted text from the PDF.
    """
    logging.info(f'Reading PDF file: {file_path}')
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ''
        for page in reader.pages:
            text += page.extract_text()
    logging.info('PDF file read successfully')
    return text

def split_text_into_chunks(text, max_chunk_size=5000):
    """Splits text into chunks of a maximum size of 5000 bytes."""
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
    """
    Function to convert text to speech using Google Cloud Text-to-Speech.
    Handles long texts by splitting into chunks.
    :param text: Text to be converted to speech.
    :param lang: Language of the text ('en-US' for English).
    :param output_file: Output file path for the wav.
    """
    client = texttospeech.TextToSpeechClient()
    logging.info('Starting text-to-speech conversion')

    def synthesize_speech_chunk(chunk, chunk_index):
        logging.info(f'Synthesizing chunk {chunk_index + 1}/{len(chunks)}')
        input_text = texttospeech.SynthesisInput(text=chunk)
        voice = texttospeech.VoiceSelectionParams(
            language_code=lang,
            name='en-US-Studio-M',  # Using a premium English Studio voice
            ssml_gender=texttospeech.SsmlVoiceGender.MALE  # Or FEMALE based on preference and availability
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

if __name__ == "__main__":
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.expanduser("~/Downloads/iconic-nimbus-423809-n0-835c178ffdfb.json")
    
    pdf_file_path = os.path.expanduser('~/Downloads/4 (1)-4.pdf')
    pdf_text = read_pdf(pdf_file_path)

    lang = 'en-US' 

    output_file = 'output.wav'
    text_to_speech(pdf_text, lang, output_file)
