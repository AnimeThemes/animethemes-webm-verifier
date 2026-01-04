"""The container format and stream information of the file being tested"""

import json
import logging
import os
import re
import subprocess


class WebmFormat:
    """The container format and stream information of the file being tested

    :param file: the file being tested
    :type file: str
    """

    format_args = [
        "ffprobe",
        "-v",
        "quiet",
        "-print_format",
        "json",
        "-show_streams",
        "-show_format",
        "-show_chapters",
    ]

    def __init__(self, file):
        self.webm_format = WebmFormat.get_webm_format(file)
        self.audio_format = WebmFormat.get_audio_format(file)
        self.loudness_stats = WebmFormat.get_loudness_stats(file)
        self.video_index = WebmFormat.get_stream_index(self.webm_format, "video")
        self.audio_index = WebmFormat.get_stream_index(self.webm_format, "audio")

    # Source 1: WebM Streams/Formats
    @staticmethod
    def get_webm_format(file):
        """Get the container format and stream information of the file

        :param file: the file being tested
        :type file: str

        :return: the container format and stream information of the file
        :rtype: dict
        """
        logging.info("Retrieving WebmM stream/format data...")

        webm_args = WebmFormat.format_args + [file]
        webm_format = subprocess.check_output(webm_args).decode("utf-8")
        return json.loads(webm_format)

    # Source 2: Extracted audio stream, needed for verifying audio bitrate
    @staticmethod
    def get_audio_format(file):
        """Get the container format and stream information of the extracted audio

        :param file: the file being tested
        :type file: str

        :return: the container format and stream information of the extracted audio
        :rtype: dict
        """
        logging.info("Retrieving extracted audio stream/format data...")

        ogg_file = f"{file}.ogg"

        ogg_args = [
            "ffmpeg",
            "-v",
            "quiet",
            "-i",
            file,
            "-vn",
            "-acodec",
            "copy",
            "-f",
            "ogg",
            "-y",
            ogg_file,
        ]

        subprocess.call(ogg_args)

        audio_args = WebmFormat.format_args + [ogg_file]
        audio_format = subprocess.check_output(audio_args).decode("utf-8")
        audio_format = json.loads(audio_format)

        os.remove(ogg_file)

        return audio_format

    # Source 3: Loudness stats
    # Implementation: https://gist.github.com/SoThatsPrettyBrutal/85cbbfc42fea03c6954d08db28c2626b
    @staticmethod
    def get_loudness_stats(file):
        """Get the loudness stats of the file

        :param file: the file being tested
        :type file: str

        :return: the loudness stats of the file
        :rtype: dict
        """
        logging.info("Retrieving loudness data...")

        loudness_args = [
            "ffmpeg",
            "-i",
            file,
            "-hide_banner",
            "-nostats",
            "-vn",
            "-sn",
            "-dn",
            "-af",
            "loudnorm=I=-16:LRA=20:TP=-1:dual_mono=true:linear=true:print_format=json",
            "-f",
            "null",
            "NUL",
        ]

        loudness_output = (
            subprocess.check_output(loudness_args, stderr=subprocess.STDOUT)
            .decode("utf-8")
            .strip()
        )

        loudness_stats = re.search(r"\{[^}]*\}", loudness_output, re.DOTALL)
        return json.loads(loudness_stats.group(0))

    # We expect video at index 0 and audio at index 1,
    # but we still want to inspect streams regardless
    @staticmethod
    def get_stream_index(webm_format, target_codec_type):
        """Get the index of the stream of a given type

        :param webm_format: the container format and stream information
        :type webm_format: dict

        :param target_codec_type: the codec type of the stream
        :type target_codec_type: str

        :return: the index of the stream of the given type
        :rtype: int
        """
        for i in range(len(webm_format["streams"])):
            codec_type = webm_format["streams"][i]["codec_type"]
            if codec_type == target_codec_type:
                return i
        return 0

    # Get entry from video stream
    def get_video_stream_entry(self, entry):
        """Get named entry from video stream

        :param entry: the name of the entry
        :type entry: str
        :return: the value of the named entry for the video stream
        :rtype: str
        """
        return self.webm_format["streams"][self.video_index].get(entry, "")

    # Get entry from audio stream
    def get_audio_stream_entry(self, entry):
        """Get named entry from audio stream

        :param entry: the name of the entry
        :type entry: str
        :return: the value of the named entry for the audio stream
        :rtype: str
        """
        return self.webm_format["streams"][self.audio_index].get(entry, "")

    # Get entry from audio format
    def get_audio_format_entry(self, entry):
        """Get named entry from audio format

        :param entry: the name of the entry
        :type entry: str
        :return: the value of the named entry for the audio format
        :rtype: str
        """
        return self.audio_format["format"].get(entry, "")

    # Get entry from loudness stats
    def get_loudness_entry(self, entry):
        """Get named entry from loudness stats

        :param entry: the name of the entry
        :type entry: str
        :return: the value of the named entry for loudness stats
        :rtype: str
        """
        return self.loudness_stats.get(entry, "")

    # Dump test data
    def debug_dump(self):
        """Log container format and stream information of the file for debugging"""
        logging.debug("Dumping test data...")
        logging.debug("video_index: '%s'", self.video_index)
        logging.debug("audio_index: '%s'", self.audio_index)
        logging.debug(
            "webm_format[streams][0][codec_type]: '%s'",
            self.webm_format["streams"][0]["codec_type"],
        )
        logging.debug(
            "webm_format[streams][1][codec_type]: '%s'",
            self.webm_format["streams"][1]["codec_type"],
        )
        logging.debug(
            "len(webm_format[streams]): '%s'", len(self.webm_format["streams"])
        )
        logging.debug(
            "webm_format[format][format_name]: '%s'",
            self.webm_format["format"]["format_name"],
        )
        logging.debug(
            "webm_format[format][bit_rate]): '%s'",
            self.webm_format["format"]["bit_rate"],
        )
        logging.debug(
            "webm_format[streams][video_index][height]: '%s'",
            self.webm_format["streams"][self.video_index]["height"],
        )
        logging.debug("webm_format[chapters]: '%s'", self.webm_format["chapters"])
        logging.debug(
            "webm_format[streams][video_index][codec_name]: '%s'",
            self.webm_format["streams"][self.video_index]["codec_name"],
        )
        logging.debug(
            "webm_format[streams][video_index][pix_fmt]: '%s'",
            self.webm_format["streams"][self.video_index]["pix_fmt"],
        )
        logging.debug(
            "webm_format[streams][video_index].get(color_space): '%s'",
            self.webm_format["streams"][self.video_index].get("color_space"),
        )
        logging.debug(
            "webm_format[streams][video_index].get(color_transfer): '%s'",
            self.webm_format["streams"][self.video_index].get("color_transfer"),
        )
        logging.debug(
            "webm_format[streams][video_index].get(color_primaries): '%s'",
            self.webm_format["streams"][self.video_index].get("color_primaries"),
        )
        logging.debug(
            "webm_format[streams][video_index][avg_frame_rate]: '%s'",
            self.webm_format["streams"][self.video_index]["avg_frame_rate"],
        )
        logging.debug(
            "webm_format[streams][audio_index][codec_name]: '%s'",
            self.webm_format["streams"][self.audio_index]["codec_name"],
        )
        logging.debug(
            "[loudness_stats] input_i: '%s', "
            "input_lra: '%s', "
            "input_tp: '%s', "
            "input_thresh: '%s', "
            "target_offset: '%s'",
            self.loudness_stats["input_i"],
            self.loudness_stats["input_lra"],
            self.loudness_stats["input_tp"],
            self.loudness_stats["input_thresh"],
            self.loudness_stats["target_offset"],
        )
        logging.debug(
            "audio_format[format][bitrate]: '%s'",
            self.audio_format["format"]["bit_rate"],
        )
        logging.debug(
            "webm_format[streams][audio_index][sample_rate]: '%s'",
            self.webm_format["streams"][self.audio_index]["sample_rate"],
        )
        logging.debug(
            "webm_format[streams][audio_index][channels]: '%s'",
            self.webm_format["streams"][self.audio_index]["channels"],
        )
        logging.debug(
            "webm_format[streams][audio_index][channel_layout]: '%s'",
            self.webm_format["streams"][self.audio_index]["channel_layout"],
        )
