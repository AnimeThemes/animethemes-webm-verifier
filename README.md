### Description

Verify WebM(s) Against AnimeThemes Encoding Standards

Executes a test suite on the input WebM(s) to verify compliance.

Test success/failure does **NOT** guarantee acceptance/rejection of submissions. In some tests, we are determining the correctness of our file properties. In other tests, we are flagging uncommon property values for inspection.

### Install

**Requirements:**

* FFmpeg
* Python >= 3.14

**Install:**

    pip install animethemes-webm-verifier

### Usage

    test_webm [-h] [--loglevel [{debug,info,error}]] [--groups [{format,video,audio} ...]] [file ...]

**File**

The WebM(s) to verify. If not provided, we will test all WebMs in the current directory.

**Groups**

The groups of tests that should be run.

The `format` group pertains to testing of the file format and context of streams.

The `video` group pertains to testing of the video stream of the file.

The `audio` group pertains to testing of the audio stream of the file.

By default, all test groups will be included.

**Logging**

Determines the level of the logging for the program.

`--loglevel error` will only output error messages.

`--loglevel info` will output error messages and script progression info messages.

`--loglevel debug` will output all messages, including variable dumps.