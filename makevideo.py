import os
from datetime import datetime, timedelta
# This import depends on the package tzdata which must be installed if it isn't already
from zoneinfo import ZoneInfo
import subprocess

video_width = 1280
video_height = 720
speed = 30  # pixels per second

# Given a recording and timestamp and duration, create a spectrum video


def duration_to_seconds(duration_str):
    split = duration_str.split(':')
    if len(split) == 1:
        return int(split[0])
    elif len(split) == 2:
        return 60 * int(split[0]) + int(split[1])
    elif len(split) == 3:
        return 3600 * int(split[0]) + 60 * int(split[1]) + int(split[2])
    raise "Cannot parse duration str: " + duration_str


def execute_ffmpeg(ffmpeg_command):
    try:
        competed_process = subprocess.run(ffmpeg_command, shell=True)
        print("Exit code:", competed_process.returncode)
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")


def create_spectrum(audio_file, start_time, end_time):
    if not os.path.exists(audio_file):
        print("File does not exist: ", audio_file)

    directory = os.path.dirname(audio_file)
    clips_directory = os.path.join(directory, "clips")
    filename = os.path.basename(audio_file)
    file_no_ext = os.path.splitext(filename)[0]

    start_time_seconds = duration_to_seconds(start_time)
    end_time_seconds = duration_to_seconds(end_time)
    clip_duration = end_time_seconds - start_time_seconds

    # Add the equivalent of screen's worth of audio to the spectrum so
    # there is something to display at the end of the video
    spectrum_width = speed * clip_duration + video_width
    adjusted_end_time = end_time_seconds + video_width / speed

    print("Spectrum width:", spectrum_width)
    print("End time:", end_time)
    print("Adjusted end time:", adjusted_end_time)

    spectrum_image = os.path.join(clips_directory, f"{file_no_ext}.png")

    ffmpeg_command = (f'ffmpeg -ss {start_time_seconds} -to {adjusted_end_time} -i "{audio_file}" '
                      f'-lavfi showspectrumpic=legend=disabled:gain=4:s={spectrum_width}x{video_height}:fscale'
                      f'=lin "{spectrum_image}" -y')

    print(ffmpeg_command)
    execute_ffmpeg(ffmpeg_command)

    return spectrum_image


def create_video(audio_file, start_time, end_time, spectrum_image):

    format_string = "%Y%m%d_%H%M%S"
    directory = os.path.dirname(audio_file)
    clips_directory = os.path.join(directory, "clips")
    filename = os.path.basename(audio_file)
    file_no_ext = os.path.splitext(filename)[0]
    video_datetime = datetime.strptime(file_no_ext, format_string).replace(tzinfo=ZoneInfo('Europe/London'))

    start_time_seconds = duration_to_seconds(start_time)
    timestamp_start = video_datetime + timedelta(seconds=start_time_seconds)

    num = 1
    while True:
        video_file = os.path.join(clips_directory, f"{file_no_ext}_{num}.mp4")
        if not os.path.exists(video_file):
            break
        num += 1

    ffmpeg_command = (f'ffmpeg -loop 1 -framerate 30 -i "{spectrum_image}" -ss {start_time} -to {end_time} -i "{audio_file}" -shortest -filter_complex '
                      f'"[0:v]crop={video_width}:{video_height}:t*{speed}:0[cropped]; [cropped]drawtext=text='
                       "'%{pts\:gmtime\:" + str(int(timestamp_start.timestamp())) + "}':fontfile=C:\\\\Windows\\\\Fonts\\\\Arial.ttf:fontsize=48:"
                       'fontcolor=white:box=1:boxcolor=black@0.5:boxborderw=5:x=50:y=50[out]" -map "[out]" '
                      f'-map 1:a -c:v libx264 -b:v 5M -movflags faststart -preset ultrafast -tune stillimage '
                      f'-pix_fmt yuv420p -c:a aac -b:a 96k -af "volume=24dB" "{video_file}" -y')

    print(ffmpeg_command)

    execute_ffmpeg(ffmpeg_command)

    return video_file


def combine_videos(audio_file, *argv):

    video_files = []
    for start_time, end_time in argv:
        print(start_time, end_time)
        spectrum_image = create_spectrum(audio_file, start_time, end_time)
        video_file = create_video(audio_file, start_time, end_time, spectrum_image)
        video_files.append(video_file)

    with open("concat.txt", "w") as f:
        for video_file in video_files:
            f.write(f"file '{video_file}'\n")

    directory = os.path.dirname(audio_file)
    filename = os.path.basename(audio_file)
    combined_file = os.path.join(directory, filename.split('_')[0] + ".mp4")
    execute_ffmpeg(f"ffmpeg -f concat -safe 0 -i concat.txt -c copy {combined_file} -y")


def dec09():
    combine_videos("C:\\Users\\alexs\\Documents\\NeighbourRecordings\\20231209_003536.3gp",
                   ("0:12:04", "0:13:06"),
                   ("02:38:51", "02:40:36"),
                   ("02:42:58", "02:43:15"),
                   ("02:45:05", "02:45:11"),
                   ("02:51:16", "02:51:33"),
                   ("03:33:43", "03:33:59"),
                   ("03:35:13", "03:35:46"),
                   ("05:24:57", "05:25:26"),
                   ("05:31:18", "05:31:31"),
                   ("06:02:41", "06:02:52"),
                   ("06:46:02", "06:46:08"),
                   ("06:52:35", "06:52:56"))


def dec10():
    combine_videos("C:\\Users\\alexs\\Documents\\NeighbourRecordings\\20231210_012326.3gp",
                   ("6:52:18", "6:52:46"),
                   ("6:53:48", "6:54:15"),
                   ("6:55:28", "6:55:57"),
                   ("6:56:43", "6:57:22"),
                   ("6:57:39", "6:57:50"),
                   ("6:59:09", "7:00:09"),
                   ("7:01:54", "7:02:38"),
                   ("7:04:45", "7:05:39"),
                   ("7:06:11", "7:06:39"),
                   ("7:07:22", "7:08:42"),
                   ("7:10:38", "7:10:43"),
                   ("7:11:13", "7:11:16"),
                   ("7:14:39", "7:14:51"),
                   ("7:17:49", "7:18:20"),
                   ("7:24:10", "7:24:14"),
                   ("7:25:38", "7:25:49"),
                   ("7:48:29", "7:49:05"),
                   ("7:52:01", "7:52:09"),
                   ("7:53:25", "7:52:30"),
                   ("8:06:02", "8:06:52"),
                   ("8:09:32", "8:09:58"),
                   ("8:38:38", "8:39:04"),
                   ("8:38:38", "8:39:04"),
                   ("8:44:43", "8:44:47"),
                   ("8:52:03", "8:52:08"),
                   ("8:54:05", "8:54:08"),
                   ("8:55:50", "8:55:52"))


def dec11():
    combine_videos("C:\\Users\\alexs\\Documents\\NeighbourRecordings\\20231211_015543.3gp",
                   ("4:15:36", "4:15:39"),
                   ("5:12:40", "5:13:01"),
                   ("5:16:25", "5:16:37"),
                   ("6:06:21", "6:06:29"),
                   ("6:15:58", "6:16:010"),
                   ("6:45:37", "6:45:43"),
                   ("7:14:20", "7:14:26"),
                   ("7:20:32", "7:20:35"),
                   ("7:30:15", "7:30:19"),
                   ("8:07:39", "8:07:42"),
                   ("8:12:55", "8:12:58"),
                   ("8:19:36", "8:19:38"))


def dec12():
    combine_videos("C:\\Users\\alexs\\Documents\\NeighbourRecordings\\20231212_004156.3gp",
                   ("4:15:36", "4:15:39"),
                   ("3:01:36", "3:01:38"),
                   ("6:20:49", "6:21:00"),
                   ("6:35:23", "6:36:44"),
                   ("6:39:17", "6:39:35"),
                   ("6:52:58", "6:53:09"),
                   ("6:53:33", "6:53:38"),
                   ("7:05:27", "7:05:35"))


def dec13():
    combine_videos("C:\\Users\\alexs\\Documents\\NeighbourRecordings\\20231213_010859.3gp",
                   ("13:05", "15:45"),
                   ("39:02", "39:10"),
                   ("5:58:08", "5:58:29"),
                   ("6:02:11", "6:02:55"),
                   ("6:04:16", "6:04:28"),
                   ("6:06:18", "6:06:31"),
                   ("6:13:04", "6:13:14"),
                   ("6:14:01", "6:14:09"),
                   ("6:17:26", "6:17:36"),
                   ("6:26:010", "6:26:14"),
                   ("6:27:05", "6:27:08"),
                   ("6:42:32", "6:42:39"),
                   ("6:45:13", "6:45:25"),
                   ("6:54:28", "6:54:34"),
                   ("7:45:21", "7:45:30"),
                   ("7:45:42", "7:45:56"),
                   ("7:46:20", "7:46:24"),
                   ("7:47:42", "7:48:15"),
                   ("7:48:43", "7:49:15"),
                   ("7:49:41", "7:59:15"),
                   ("7:59:34", "8:01:29"),
                   ("8:01:59", "8:03:54"),
                   ("8:04:14", "8:07:14"),
                   ("8:07:49", "8:09:44"),
                   ("8:10:39", "8:12:25"),
                   ("8:14:09", "8:14:46"),
                   ("8:40:04", "8:42:54"))


dec11()
dec12()
dec13()
