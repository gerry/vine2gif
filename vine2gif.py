#!/usr/bin/env python
# Convert Vine URL's into animated GIF's
# BE WARNED! This is only ment to be a toy.
#
# @gerryeisenhaur
import re
import os
import sys
import envoy
import shutil
import tempfile
import requests

ffmpeg_path = "/Users/gerry/bin/ffmpeg"
convert_path = "/usr/local/bin/convert"
frame_rate = 6


def download_movie(vine_url):
    (movie_file, movie_path) = tempfile.mkstemp()
    r = requests.get(vine_url)
    if r.status_code != 200:
        print r.status_code, r.error
        return None

    match = re.search('<source.*src="([^\s]*)"', r.content)
    if not match:
        return None

    movie_url = match.groups()[0]
    r = requests.get(movie_url)
    if r.status_code != 200:
        print r.status_code, r.error
        return None

    os.fdopen(movie_file, 'wb').write(r.content)
    return movie_path


def make_gif(movie_path, output_name):
    outpath = tempfile.mkdtemp()
    ffmpeg_cmd = "%s -i %s -r %d %s/output%%05d.png" % (ffmpeg_path,
            movie_path, frame_rate, outpath)
    envoy.run(ffmpeg_cmd)

    if not output_name.endswith(".gif"):
        output_name += ".gif"
    convert_cmd = str("%s -resize 50%% %s/output*.png %s" % (convert_path,
        outpath, output_name))
    envoy.run(convert_cmd)

    shutil.rmtree(outpath)
    return output_name


def main():
    if len(sys.argv) != 3:
        print "USAGE: %s <vine_url> <output_name>" % sys.argv[0]
        sys.exit(-1)

    vine_url = sys.argv[1]
    output_name = sys.argv[2]
    if not vine_url.startswith("http"):
        vine_url = "https://" + vine_url
    movie_path = download_movie(vine_url)
    make_gif(movie_path, output_name)

if __name__ == "__main__":
    main()
