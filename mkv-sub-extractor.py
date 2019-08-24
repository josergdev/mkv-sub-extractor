import subprocess
import json
import os
import sys
from subprocess import Popen, PIPE
from tqdm import tqdm


def get_info_from_mkv(mkv_file):
    output = subprocess.run(
        ["mkvmerge", "-i", mkv_file, "-F", "json"], capture_output=True)
    if output.stderr:
        print("STDERR", output.stderr)
    if output.stdout:
        info = json.loads(output.stdout)
    return info


def extract_srt_from_mkv(mkv_info):
    mkv_file = mkv_info["file_name"]
    name = os.path.splitext(mkv_file)[0]

    tracks = mkv_info["tracks"]
    sub_tracks = list(
        filter(lambda track: track["codec"] == "SubRip/SRT", tracks))
    parsed_sub_tracks = list(map(lambda sub_track:
                                 "{}:{}.{}.{}{}_{}.srt"
                                 .format(
                                     sub_track["id"],
                                     name,
                                     sub_track["properties"]["language"],
                                     "forced."
                                     if sub_track["properties"]["forced_track"]
                                     else "",
                                     sub_track["id"],
                                     sub_track["properties"]["track_name"]
                                 ),
                                 sub_tracks))
    with Popen(["mkvextract", mkv_file, "tracks"] + parsed_sub_tracks,
               stdout=PIPE, bufsize=1,
               universal_newlines=True) as p:
        pbar = tqdm(total=100)
        for line in p.stdout:
            if "Progress: " in line:
                prog_n = int(''.join(x for x in line if x.isdigit()))
                pbar.update(prog_n - pbar.n)
        pbar.close()


if __name__ == "__main__":
    # mkv_path = ("/Volumes/macOS HD/jose/Documents/prueba_mkv/"
    #            "Stranger Things 2x01 MADMAX [WEBRip 720p x264"
    #            " Dual AC3 5.1 Subs][GrupoHDS].mkv")
    # extract_srt_from_mkv(mkv_file=mkv_path, track_id=3)
    mkv_path = sys.argv[1]
    info = get_info_from_mkv(mkv_file=mkv_path)
    extract_srt_from_mkv(mkv_info=info)
