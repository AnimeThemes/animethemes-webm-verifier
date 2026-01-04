"""A collection of tests to verify the file against format encoding standards"""

from packaging import version
from ._test_webm import TestWebm


class TestFormat(TestWebm):
    """A collection of tests to verify the file against format encoding standards"""

    # Expectation 1: Index 0 stream is video
    def test_video_stream(self):
        """Test if the video stream is first indexed stream"""
        first_stream_codec = self.webm_format.webm_format["streams"][0]["codec_type"]
        self.assertEqual(first_stream_codec, "video", "First stream is not video")

    # Expectation 2: Index 1 stream is audio
    def test_audio_stream(self):
        """Test if the audio stream is second indexed stream"""
        second_stream_codec = self.webm_format.webm_format["streams"][1]["codec_type"]
        self.assertEqual(second_stream_codec, "audio", "Second stream is not audio")

    # Expectation 3: There exists 1 video stream and 1 audio stream
    def test_stream_count(self):
        """Test if the file has exactly two streams"""
        streams = len(self.webm_format.webm_format["streams"])
        self.assertEqual(streams, 2, "Unexpected number of streams")

    # Files must use the latest release version of FFmpeg.
    def test_encoder_name(self):
        """Test if the encoder is FFmpeg"""
        for tag_key in self.webm_format.webm_format["format"]["tags"]:
            if tag_key.lower() == "encoder":
                encoder = self.webm_format.webm_format["format"]["tags"][tag_key]
                self.assertTrue(encoder.startswith("Lavf"), "Incorrect Encoder")

    # Files must use the latest release version of FFmpeg.
    def test_encoder_version(self):
        """Test if the FFmpeg build is out of date"""
        for tag_key in self.webm_format.webm_format["format"]["tags"]:
            if tag_key.lower() == "encoder":
                # FFmpeg versioning doesn't comply with PEP 440 so we can't use packaging.version
                webm_ffmpeg_version = version.parse(
                    self.webm_format.webm_format["format"]["tags"][
                        tag_key
                    ].removeprefix("Lavf")
                )
                latest_ffmpeg_version = version.parse("61.7.100")
                self.assertTrue(
                    webm_ffmpeg_version >= latest_ffmpeg_version, "Build is out of date"
                )

    # Files must use the WebM container.
    def test_file_format(self):
        """Test if the file format is webm"""
        webm_format = self.webm_format.webm_format["format"]["format_name"]
        self.assertEqual(webm_format, "matroska,webm", "Incorrect file format")

    # Files must adhere to our size restrictions.
    def test_filesize(self):
        """Test if the file size violates an approximation of the restrictions"""
        bit_rate = int(self.webm_format.webm_format["format"]["bit_rate"])
        resolution = int(self.webm_format.get_video_stream_entry("height"))
        # Linear fit approximation, we just want to flag egregious overall bitrates here
        self.assertTrue(
            bit_rate < resolution * 5000 + 683300, "File size restriction violated"
        )

    # Files must erase source metadata using -map_metadata -1.
    def test_metadata(self):
        """Test if extraneous source file metadata exists"""
        found_source_metadata = False

        for stream in self.webm_format.webm_format["streams"]:
            # Tag entry isn't guaranteed to exist, examples found in VP8 encodes
            for tag_key in stream.get("tags", []):
                if tag_key.lower() != "encoder" and tag_key.lower() != "duration":
                    found_source_metadata = True

        # Tag entry is expected to exist here, haven't found examples where that isn't true
        for tag_key in self.webm_format.webm_format["format"]["tags"]:
            if tag_key.lower() != "encoder":
                found_source_metadata = True

        self.assertFalse(found_source_metadata, "Extraneous source file metadata")

    # Files must erase source menu data using -map_chapters -1.
    def test_chapters(self):
        """Test if menu data exists"""
        self.assertTrue(
            not self.webm_format.webm_format["chapters"], "Extraneous menu data"
        )
