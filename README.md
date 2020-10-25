### Description

Verify WebM(s) Against AnimeThemes Encoding Standards

Executes a test suite on the input WebM(s) to verify compliance.

Test success/failure does **NOT** guarantee acceptance/rejection of submissions. In some tests, we are determining the correctness of our file properties. In other tests, we are flagging uncommon property values for inspection.

### Install

**Requirements:**

* FFmpeg
* Python >= 3.6

**Install:**

    pip install animethemes-webm-verifier

### Usage

    python -m test_webm [-h] [--loglevel [{debug,info,error}] [file [file ...]]

* `--loglevel error`: Only show error messages
* `--loglevel info`: Show error messages and script progression info messages
* `--loglevel debug`: Show all messages, including variable dumps
* `[file ...]`: The WebM(s) to verify. If not provided, we will test all WebMs in the current directory.