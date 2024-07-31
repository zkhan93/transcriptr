import collections
import os
import wave
import pyaudio
import webrtcvad
from datetime import datetime
from loguru import logger
import time
RESPEAKER_RATE = 16000
RESPEAKER_CHANNELS = 1
RESPEAKER_WIDTH = 2
MAX_FILE_SIZE = 24 * 1024 * 1024  # 24 MB
FRAME_DURATION_MS = 30  # Frame duration in milliseconds

class VoiceActivityRecorder:
    def __init__(self, directory, sample_rate=RESPEAKER_RATE, segment_duration=60):
        self.directory = directory
        self.sample_rate = sample_rate
        self.segment_duration = segment_duration
        self.channels = RESPEAKER_CHANNELS
        self.frame_duration = FRAME_DURATION_MS
        self.chunk = int(self.sample_rate * (self.frame_duration / 1000))
        logger.info(f"chunk size: {self.chunk}")
        self.vad = webrtcvad.Vad(1)
        self.audio = pyaudio.PyAudio()
        self.format = self.audio.get_format_from_width(RESPEAKER_WIDTH)
        self.input_device_index = 1

    def open_stream(self):
        return self.audio.open(format=self.format, channels=self.channels,
                               rate=self.sample_rate, input=True,
                               frames_per_buffer=self.chunk, input_device_index=self.input_device_index)

    def start_new_recording(self):
        output_file = os.path.join(self.directory, datetime.now().strftime('%Y-%m-%d_%H-%M-%S.wav'))
        wav_writer = wave.open(output_file, 'wb')
        wav_writer.setnchannels(self.channels)
        wav_writer.setsampwidth(self.audio.get_sample_size(self.format))
        wav_writer.setframerate(self.sample_rate)
        logger.info(f"Recording to {output_file}")
        return wav_writer, output_file

    def close_recording(self, wav_writer, output_file):
        if wav_writer:
            wav_writer.close()
            logger.info(f"Saved recording to {output_file}")

    def record_audio(self):
        stream = self.open_stream()
        logger.info(f"max len {int(self.sample_rate / self.chunk * self.segment_duration)}")
        frames = collections.deque(maxlen=int(self.sample_rate / self.chunk * self.segment_duration))
        recording = False
        output_file = None
        wav_writer = None
        file_size = 0
        try:
            logger.info("starting...")
            last_speech_time = 0
            last_recording_start_time = 0
            last_log_time = 0
            wav_writer, output_file = self.start_new_recording()
            while True:
                frame = stream.read(self.chunk, exception_on_overflow=True)
                is_speech = self.vad.is_speech(frame, self.sample_rate)
                time_since_last_speech = int(time.time() - last_speech_time)
                recording_since = int(time.time() - last_recording_start_time)
                time_to_log = int(time.time() - last_log_time) >= 15
                if time_to_log:
                    logger.info(f"speech: {is_speech}, recording: {recording} | {time_since_last_speech}s since last speech, {recording_since}s since recording started, {file_size//1024} KB")
                    last_log_time = time.time()
                if is_speech:
                    last_speech_time = time.time()
                    if not recording:  
                        recording = True
                        last_recording_start_time = time.time()
                
                if recording:
                    frames.append(frame)
                    file_size += len(frame)

                    max_file_size_reached = file_size >= MAX_FILE_SIZE
                    max_recording_time_reached = int(time.time() - last_recording_start_time) >= self.segment_duration
                    if max_file_size_reached or max_recording_time_reached:
                        logger.info("closing file as max file size or max recording time reached")
                        wav_writer.writeframes(b''.join(frames))
                        self.close_recording(wav_writer, output_file)
                        wav_writer, output_file = self.start_new_recording()
                        frames.clear()
                        file_size = 0

                    # if no speech was found for 1 minute after the last_speech_time
                    should_stop_recording = (time.time() - last_speech_time) >= 10
                    if should_stop_recording:
                        recording = False

        except Exception as e:
            logger.exception(f"Exception occurred: {e}")
            wav_writer.writeframes(b''.join(frames))
            self.close_recording(wav_writer, output_file)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Voice Activity Recorder')
    parser.add_argument('-d', '--directory', required=True, help='Directory to place the recorded files')
    parser.add_argument('-t', '--segment_duration', type=int, default=60, help='Duration of each segment in seconds')

    args = parser.parse_args()

    os.makedirs(args.directory, exist_ok=True)
    recorder = VoiceActivityRecorder(directory=args.directory, segment_duration=args.segment_duration)
    recorder.record_audio()
