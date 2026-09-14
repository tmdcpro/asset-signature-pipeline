import subprocess, os, json

VIDEO_DIR = "/home/user/workspace/video"
FRAMES = f"{VIDEO_DIR}/frames"
AUDIO = f"{VIDEO_DIR}/audio"
WORK = f"{VIDEO_DIR}/work"
os.makedirs(WORK, exist_ok=True)

SLIDES = ["01_intro", "02_config", "03_returnrisk", "04_shape", "05_beta",
          "06_dynamics", "07_bondoption", "08_run", "09_outro"]

PAD = 0.45  # silence padding appended after each narration segment


def run(cmd):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if r.returncode != 0:
        print("CMD FAILED:", cmd)
        print(r.stderr[-3000:])
        raise SystemExit(1)
    return r.stdout


def ffprobe_duration(path):
    out = run(f'ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "{path}"')
    return float(out.strip())


segments = []
for name in SLIDES:
    src_audio = f"{AUDIO}/{name}.mp3"
    padded_audio = f"{WORK}/{name}_padded.mp3"
    run(f'ffmpeg -y -i "{src_audio}" -af "apad=pad_dur={PAD}" -c:a mp3 "{padded_audio}"')
    dur = ffprobe_duration(padded_audio)

    img = f"{FRAMES}/{name}.png"
    clip = f"{WORK}/{name}_clip.mp4"
    run(
        f'ffmpeg -y -loop 1 -i "{img}" -t {dur:.3f} '
        f'-vf "scale=1920:1080,format=yuv420p" -r 30 '
        f'-c:v libx264 -preset fast -crf 23 -pix_fmt yuv420p "{clip}"'
    )
    segments.append({"name": name, "audio": padded_audio, "video": clip, "duration": dur})
    print(name, "duration:", round(dur, 2))

# concat list files
with open(f"{WORK}/videos.txt", "w") as f:
    for s in segments:
        f.write(f"file '{s['video']}'\n")
with open(f"{WORK}/audios.txt", "w") as f:
    for s in segments:
        f.write(f"file '{s['audio']}'\n")

run(f'ffmpeg -y -f concat -safe 0 -i "{WORK}/videos.txt" -c copy "{WORK}/silent_video.mp4"')
run(f'ffmpeg -y -f concat -safe 0 -i "{WORK}/audios.txt" -c copy "{WORK}/full_narration.mp3"')

total_dur = sum(s["duration"] for s in segments)
print("Total duration (s):", round(total_dur, 2))

fade_out_start = max(total_dur - 0.6, 0)
run(
    f'ffmpeg -y -i "{WORK}/silent_video.mp4" -i "{WORK}/full_narration.mp3" '
    f'-vf "fade=t=in:st=0:d=0.5,fade=t=out:st={fade_out_start:.3f}:d=0.6" '
    f'-c:v libx264 -preset fast -crf 22 -pix_fmt yuv420p '
    f'-c:a aac -b:a 192k -shortest '
    f'"{VIDEO_DIR}/asset_signature_pipeline_demo.mp4"'
)

print("DONE:", f"{VIDEO_DIR}/asset_signature_pipeline_demo.mp4")
