import queue
import re
import sys

from google.cloud import speech

import pyaudio

# Audio recording parameters
AUDIO_RATE = 16000
AUDIO_CHUNK = int(AUDIO_RATE / 10)  # 100ms


class MicrophoneStream:
    """Opens a recording stream as a generator yielding the audio chunks.
    Reference: https://cloud.google.com/speech-to-text/docs/samples/speech-transcribe-streaming-mic?hl=en
    """

    def __init__(self: object, rate: int = AUDIO_RATE, chunk: int = AUDIO_CHUNK) -> None:
        """The audio -- and generator -- is guaranteed to be on the main thread."""
        self._rate = rate
        self._chunk = chunk

        # Create a thread-safe buffer of audio data
        self._buff = queue.Queue()
        self.closed = True

    def __enter__(self: object) -> object:
        self._audio_interface = pyaudio.PyAudio()
        self._audio_stream = self._audio_interface.open(
            format=pyaudio.paInt16,
            # The API currently only supports 1-channel (mono) audio
            # https://goo.gl/z757pE
            channels=1,
            rate=self._rate,
            input=True,
            frames_per_buffer=self._chunk,
            # Run the audio stream asynchronously to fill the buffer object.
            # This is necessary so that the input device's buffer doesn't
            # overflow while the calling thread makes network requests, etc.
            stream_callback=self._fill_buffer,
        )

        self.closed = False

        return self

    def __exit__(
        self: object,
        type: object,
        value: object,
        traceback: object,
    ) -> None:
        """Closes the stream, regardless of whether the connection was lost or not."""
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self.closed = True
        # Signal the generator to terminate so that the client's
        # streaming_recognize method will not block the process termination.
        self._buff.put(None)
        self._audio_interface.terminate()

    def _fill_buffer(
        self: object,
        in_data: object,
        frame_count: int,
        time_info: object,
        status_flags: object,
    ) -> object:
        """Continuously collect data from the audio stream, into the buffer.

        Args:
            in_data: The audio data as a bytes object
            frame_count: The number of frames captured
            time_info: The time information
            status_flags: The status flags

        Returns:
            The audio data as a bytes object
        """
        self._buff.put(in_data)
        return None, pyaudio.paContinue

    def generator(self: object) -> object:
        """Generates audio chunks from the stream of audio data in chunks.

        Args:
            self: The MicrophoneStream object

        Returns:
            A generator that outputs audio chunks.
        """
        while not self.closed:
            # Use a blocking get() to ensure there's at least one chunk of
            # data, and stop iteration if the chunk is None, indicating the
            # end of the audio stream.
            chunk = self._buff.get()
            if chunk is None:
                return
            data = [chunk]

            # Now consume whatever other data's still buffered.
            while True:
                try:
                    chunk = self._buff.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break

            yield b"".join(data)

def get_final_transcription(responses: object) -> str:
    """Processes speech recognition responses and returns the final transcription.

    Monitors the incoming stream of recognition responses until a final result
    is received. While waiting for the final result, displays interim transcriptions
    in place using carriage returns.

    Args:
        responses: Generator of google.cloud.speech.StreamingRecognizeResponse objects

    Returns:
        transcript: The final transcription text once a complete utterance is recognized.
    """
    transcript = ""
    for response in responses:
        if not response.results:
            continue

        # The `results` list contains consecutive results. We only process
        # the first result since we're waiting for a final transcription.
        result = response.results[0]
        if not result.alternatives:
            continue

        # Display the transcription of the top alternative.
        transcript = result.alternatives[0].transcript

        if result.is_final:
            return transcript

    return transcript