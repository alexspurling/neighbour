import os
from datetime import datetime, timedelta
# This import depends on the package tzdata which must be installed if it isn't already
from zoneinfo import ZoneInfo
import subprocess


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
    filename = os.path.basename(audio_file)
    file_no_ext = os.path.splitext(filename)[0]

    spectrum_width = 8640

    spectrum_image = f"{directory}/{file_no_ext}_python.png"

    ffmpeg_command = (f'ffmpeg -ss {start_time} -to {end_time} -i "{audio_file}" '
                      f'-lavfi showspectrumpic=legend=disabled:gain=4:s={spectrum_width}x720:fscale'
                      f'=lin "{spectrum_image}" -y')

    print(ffmpeg_command)
    execute_ffmpeg(ffmpeg_command)

    create_video(audio_file, start_time, end_time, spectrum_image, spectrum_width)


def create_video(audio_file, start_time, end_time, spectrum_image, spectrum_width):

    start_time_seconds = duration_to_seconds(start_time)
    end_time_seconds = duration_to_seconds(end_time)
    clip_duration = end_time_seconds - start_time_seconds

    scroll_pixels_per_second = spectrum_width / clip_duration

    print("Clip duration:", clip_duration)
    print("Pixels per second:", scroll_pixels_per_second)

    format_string = "%Y%m%d_%H%M%S"
    directory = os.path.dirname(audio_file)
    filename = os.path.basename(audio_file)
    file_no_ext = os.path.splitext(filename)[0]
    video_datetime = datetime.strptime(file_no_ext, format_string).replace(tzinfo=ZoneInfo('Europe/London'))

    timestamp_start = video_datetime + timedelta(seconds=start_time_seconds)

    video_file = f"{directory}/{file_no_ext}_python.mp4"

    ffmpeg_command = (f'ffmpeg -loop 1 -framerate 30 -i "{spectrum_image}" -ss {start_time} -to {end_time} -i "{audio_file}" -shortest -filter_complex '
                      f'"color=c=black:s=1280x720:r=30[black]; [0:v][black]hstack[stacked]; [stacked]crop=1280:720:t*{scroll_pixels_per_second}:0[cropped]; [cropped]drawtext=text='
                       "'%{pts\:gmtime\:" + str(int(timestamp_start.timestamp())) + "}':fontfile=C:\\\\Windows\\\\Fonts\\\\Arial.ttf:fontsize=48:"
                       'fontcolor=white:box=1:boxcolor=black@0.5:boxborderw=5:x=50:y=50[out]" -map "[out]" '
                      f'-map 1:a -c:v libx264 -b:v 5M -movflags faststart -preset ultrafast -tune stillimage '
                      f'-pix_fmt yuv420p "{video_file}" -c:a aac -b:a 128k -y')

    print(ffmpeg_command)

    execute_ffmpeg(ffmpeg_command)


create_spectrum("C:\\Users\\alexs\\Documents\\NeighbourRecordings\\20231108_002137.3gp", "6:47:50", "6:56:56")

# create_video("C:\\Users\\alexs\\Documents\\NeighbourRecordings\\20231108_002137.3gp", "6:47:50", "6:56:56",
#              "C:\\Users\\alexs\\Documents\\NeighbourRecordings\\20231108_002137_python.png", 12960)

# create_spectrum("C:\\Users\\alexs\\Documents\\NeighbourRecordings\\20231213_010859.wav", "35", "1:35")
