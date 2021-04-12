"""A collection of tests to verify the file against audio encoding standards"""

from ._test_webm import TestWebm


class TestAudio(TestWebm):
    """A collection of tests to verify the file against audio encoding standards"""

    # Audio must use the Opus format.
    def test_audio_codec(self):
        """Test if the audio codec is opus"""
        audio_codec = self.webm_format.get_audio_stream_entry('codec_name')
        self.assertEqual(audio_codec, 'opus', 'Incorrect audio codec')

    # Audio must be normalized as described by the AES Streaming Loudness Recommendation.
    def test_loudness_i(self):
        """Test if the average perceptual loudness is near the targeted -16 LUFS"""
        input_i = float(self.webm_format.get_loudness_entry('input_i'))
        self.assertTrue(-16.25 <= input_i <= -15.75, 'Unexpected target loudness')

    # Audio must be normalized as described by the AES Streaming Loudness Recommendation.
    def test_loudness_tp(self):
        """Test if the true peak of the audio stream is less than -1.0 dB"""
        input_tp = float(self.webm_format.get_loudness_entry('input_tp'))
        self.assertTrue(input_tp <= -1.0, 'Unexpected true peak')

    # If the source is a DVD or BD release with a source bitrate of >= 320 kbps,
    # the audio stream must use a bitrate of 320 kbps.
    # Otherwise, the audio stream must use a default bitrate of 192 kbps.
    def test_audio_bitrate(self):
        """Test if the audio bitrate is near the targeted 192 kbps or 320 kbps"""
        # Note: libopus defaults to VBR mode so we will allow for variance
        audio_bitrate = int(self.webm_format.get_audio_format_entry('bit_rate'))
        self.assertTrue(
            167000 <= audio_bitrate <= 217000 or 295000 <= audio_bitrate <= 345000,
            'Unexpected audio bitrate'
        )

    # Audio must use a sampling rate of 48k.
    def test_sample_rate(self):
        """Test if the sampling rate is 48 kHz"""
        sample_rate = int(self.webm_format.get_audio_stream_entry('sample_rate'))
        self.assertEqual(sample_rate, 48000, 'Incorrect sample rate')

    # Audio must use a two channel stereo mix.
    def test_channels(self):
        """Test if there exists two audio channels"""
        channels = int(self.webm_format.get_audio_stream_entry('channels'))
        self.assertEqual(channels, 2, 'Incorrect audio channels')

    # Audio must use a two channel stereo mix.
    def test_layout(self):
        """Test if the audio layout is stereo"""
        channel_layout = self.webm_format.get_audio_stream_entry('channel_layout')
        self.assertEqual(channel_layout, 'stereo', 'Incorrect audio layout')
