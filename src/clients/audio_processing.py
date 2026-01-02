from faster_whisper import WhisperModel
import json
import vosk
import numpy as np
import soundfile as sf


# How many seconds of the audio is used for language detection
HEAD_DURATION = 5

VOSK_EN_MODEL_DIR = "models/audio_processing/vosk-model-small-en-us-0.15"
VOSK_PL_MODEL_DIR = "models/audio_processing/vosk-model-small-pl-0.22"
VOSK_RU_MODEL_DIR = "models/audio_processing/vosk-model-small-ru-0.22"

# Disable Vosk logs
vosk.SetLogLevel(-1)


# read the audio
def read_audio(file_path):
    data, sample_rate = sf.read(file_path)
    data = np.int16(data * 32767)
    data = data.tobytes()
    return data


class TranscriptionModel(object):
    def transcript_audio(self, audio_file_path):
        pass


class VoskTranscriptionModel(TranscriptionModel):
    def __init__(self, model_path, sample_rate=16000):
        super().__init__()
        self.model = vosk.Model(model_path)
        self.recognizer = vosk.KaldiRecognizer(self.model, sample_rate)

    def transcript_audio(self, audio_file_path):
        print(audio_file_path)
        audio_data = read_audio(audio_file_path)
        self.recognizer.AcceptWaveform(audio_data)
        result = self.recognizer.Result()
        res_text = json.loads(result).get("text", "")
        return res_text


class AudioTranscriptionClient:
    def transcript(self, audio_file) -> dict:
        raise NotImplementedError


#  AutoLangAudioTranscriptionClient class
class AutoLangAudioTranscriptionClient(AudioTranscriptionClient):
    def __init__(self):
        super().__init__()
        self.detection_model = WhisperModel("tiny", device="cpu", compute_type="int8")
        self.head_duration = HEAD_DURATION
        self.transcription_models = {
            "en": VoskTranscriptionModel(VOSK_EN_MODEL_DIR),
            "pl": VoskTranscriptionModel(VOSK_PL_MODEL_DIR),
            "ru": VoskTranscriptionModel(VOSK_RU_MODEL_DIR),
        }

    def get_language(self, audio_file_path):
        _, info = self.detection_model.transcribe(
            audio_file_path,
            language=None,
            clip_timestamps=[0.0, HEAD_DURATION],
            vad_filter=True,
        )
        return info.language

    def transcript(self, audio_file):
        language = self.get_language(audio_file)
        if not language in self.transcription_models:
            print(f"Unknown language: {language}")
            return ""

        transcription_model = self.transcription_models[language]

        text = transcription_model.transcript_audio(audio_file)
        return text
