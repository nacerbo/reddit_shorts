from azure.cognitiveservices.speech import AudioDataStream, SpeechConfig, SpeechSynthesizer, SpeechSynthesisOutputFormat
from azure.cognitiveservices.speech.audio import AudioOutputConfig


def generate_audio(text, filename):
    speech_config = SpeechConfig(subscription="", region="westeurope")
    audio_config = AudioOutputConfig(use_default_speaker=True)
    speech_config.set_speech_synthesis_output_format(SpeechSynthesisOutputFormat["Audio48Khz192KBitRateMonoMp3"]) #Riff24Khz16BitMonoPcm
    speech_config.speech_synthesis_voice_name = 'en-CA-LiamNeural'
    synthesizer = SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
    result = synthesizer.speak_text_async(text).get()
    stream = AudioDataStream(result)
    print("generating audio {}".format(filename))
    stream.save_to_wav_file(filename)

