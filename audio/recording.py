import speech_recognition as sr 
import os 
from pydub import AudioSegment
from pydub.silence import split_on_silence

# create a speech recognition object
r = sr.Recognizer()

# a function to recognize speech in the audio file
# so that we don't repeat ourselves in in other functions
def transcribe_audio(path):
    # use the audio file as the audio source
    with sr.AudioFile(path) as source:
        audio_listened = r.record(source)
        # try converting it to text
        text = r.recognize_google(audio_listened)
    return text

# a function that splits the audio file into chunks on silence
# and applies speech recognition
def get_large_audio_transcription_on_silence(path):
    """Splitting the large audio file into chunks
    and apply speech recognition on each of these chunks"""
    # open the audio file using pydub
    sound = AudioSegment.from_file(path)  
    # split audio sound where silence is 500 miliseconds or more and get chunks
    chunks = split_on_silence(sound,
        # experiment with this value for your target audio file
        min_silence_len = 500,
        # adjust this per requirement
        silence_thresh = sound.dBFS-14,
        # keep the silence for 1 second, adjustable as well
        keep_silence=500,
    )
    folder_name = "audio-chunks"
    # create a directory to store the audio chunks
    if not os.path.isdir(folder_name):
        os.mkdir(folder_name)
    whole_text = ""
    # process each chunk 
    for i, audio_chunk in enumerate(chunks, start=1):
        # export audio chunk and save it in
        # the `folder_name` directory.
        chunk_filename = os.path.join(folder_name, f"chunk{i}.wav")
        audio_chunk.export(chunk_filename, format="wav")
        # recognize the chunk
        try:
            text = transcribe_audio(chunk_filename)
        except sr.UnknownValueError as e:
            print("Error:", str(e))
        else:
            text = f"{text.capitalize()}. "
            print(chunk_filename, ":", text)
            whole_text += text
    # return the text for all chunks detected
    return whole_text


def record_from_mic(filename: str, duration: float = None) -> None:
    """
    Record audio from the default microphone and write it to `filename`.
    If `duration` is given it stops after that many seconds,
    otherwise it waits until the user pauses.
    """
    with sr.Microphone() as mic:
        r.adjust_for_ambient_noise(mic)      # optional: reduce background noise
        print("Recording… speak now")
        audio = r.listen(mic, timeout=duration, phrase_time_limit=duration)
    # write to WAV so the rest of your code can process it
    with open(filename, "wb") as f:
        f.write(audio.get_wav_data())
    print(f"Saved recording to {filename}")


def record_and_transcribe():
    """convenience: record then run your existing transcription routine"""
    temp = "temp.wav"
    record_from_mic(temp, duration=5)          # record 5 seconds (or omit)
    text = transcribe_audio(temp)              # from your file-based helper
    print("You said:", text)
    print("creating notes based on recording...")


# --- simple start/stop recorder using pyaudio ---
import threading
import pyaudio
import wave

class AudioRecorder:
    """Basic threaded recorder writing to a WAV file."""
    def __init__(self, filename="temp.wav", rate=44100, channels=1, frames_per_buffer=1024):
        self.filename = filename
        self.rate = rate
        self.channels = channels
        self.format = pyaudio.paInt16
        self.frames_per_buffer = frames_per_buffer
        self._running = False
        self._pa = pyaudio.PyAudio()
        self.frames = []
        self.stream = None

    def start(self):
        if self._running:
            return
        try:
            self.stream = self._pa.open(format=self.format,
                                        channels=self.channels,
                                        rate=self.rate,
                                        input=True,
                                        frames_per_buffer=self.frames_per_buffer)
        except Exception as e:
            print("Failed to open audio stream:", e)
            return
        self._running = True
        self.frames = []
        threading.Thread(target=self._record, daemon=True).start()
        print("Recording started")

    def _record(self):
        while self._running:
            try:
                data = self.stream.read(self.frames_per_buffer, exception_on_overflow=False)
            except Exception as e:
                # stop if the stream is closed or host error occurs
                print("Recording thread error:", e)
                break
            self.frames.append(data)

    def stop(self):
        if not self._running:
            return
        self._running = False
        self.stream.stop_stream()
        self.stream.close()
        self.stream = None
        wf = wave.open(self.filename, 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(self._pa.get_sample_size(self.format))
        wf.setframerate(self.rate)
        wf.writeframes(b''.join(self.frames))
        wf.close()
        print(f"Recording stopped, saved to {self.filename}")

# global recorder instance for toggle
_recorder = None

def toggle_recording(filename="temp.wav"):
    """Start or stop recording, return current state ('started' or 'stopped')."""
    global _recorder
    if _recorder is None:
        _recorder = AudioRecorder(filename=filename)
        _recorder.start()
        return "started"
    else:
        _recorder.stop()
        _recorder = None
        return "stopped"


if __name__ == "__main__":
    record_and_transcribe()