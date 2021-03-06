"""Main class for bot."""

import os
import time

import botskeleton
from PIL import Image

import album_art_gen

# Delay between tweets in seconds.
DELAY = 3600

ALBUM_ART_FILENAME = album_art_gen.ALBUM_ART_FILENAME
MAX_IMAGE_SIZE_BYTES = 3072 * 1024

if __name__ == "__main__":
    SECRETS_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), "SECRETS")
    BOT_SKELETON = botskeleton.BotSkeleton(SECRETS_DIR, bot_name="isthisska_bot", delay=DELAY)
    LOG = BOT_SKELETON.log

    while True:
        LOG.info("Grabbing random album art from Musicbrainz.")
        try:
            info = album_art_gen.produce_random_album_art()

        except album_art_gen.APIException as e:
            LOG.error("Encountered an API Exception.")
            LOG.error(f"Code: {e.code} Message: {e.message}")

            if e.code == 503:
                LOG.error("API error or rate limiting - waiting at least a few minutes.")
                time.sleep(300)
            LOG.error("Restarting from the beginning.")
            continue

        LOG.info("Sending tweet with art.")

        LOG.info(f"Check size of file (must be <{MAX_IMAGE_SIZE_BYTES} to send)")
        file_size = os.path.getsize(album_art_gen.ALBUM_ART_PATH)
        LOG.info(f"Size of {album_art_gen.ALBUM_ART_PATH} is {file_size}")
        while file_size >= MAX_IMAGE_SIZE_BYTES:
            LOG.info(f"Size is {file_size}, bigger than {MAX_IMAGE_SIZE_BYTES}."
                     "Resizing, retrying.")
            im = Image.open(album_art_gen.ALBUM_ART_PATH)
            im = im.resize((im.width//2, im.height//2), Image.ANTIALIAS)

            im.save(album_art_gen.ALBUM_ART_PATH)

            file_size = os.path.getsize(album_art_gen.ALBUM_ART_PATH)
            LOG.info(f"Size after save, before loop restart, is {file_size}")

            LOG.info("Retrying tweet.")

        LOG.info("Sending out album art.")
        BOT_SKELETON.send_with_one_media(
            (
                f"Is {info['album']} by {info['artist']} ska?"
                f"\n(MB Release: https://musicbrainz.org/release/{info['release_id']})"
            ),
            album_art_gen.ALBUM_ART_PATH,
            f"Cover art for the album {info['album']} by the artist {info['artist']}"
        )

        BOT_SKELETON.nap()

