"""Main class for bot."""

import os
import subprocess
import time

import botskeleton
import tweepy

import album_art_gen

# Delay between tweets in seconds.
DELAY = 1800 # half hour

ALBUM_ART_FILENAME = album_art_gen.ALBUM_ART_FILENAME
TWEET_TEXT = "Is this ska?\n(MB Release: https://musicbrainz.org/release/{})"
MAX_IMAGE_SIZE_BYTES = 3072 * 1024

if __name__ == "__main__":
    SECRETS_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), "SECRETS")
    api = botskeleton.BotSkeleton(SECRETS_DIR, bot_name="isthisska_bot")

    LOG = botskeleton.set_up_logging()

    while True:
        LOG.info("Grabbing random album art from Musicbrainz.")
        try:
            id = album_art_gen.produce_random_album_art()

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
        if file_size >= MAX_IMAGE_SIZE_BYTES:
            LOG.info("Too big, shrinking.")
            LOG.info("Running shrink commands.")
            subprocess.run(["convert", album_art_gen.ALBUM_ART_PATH, "-resize", "50%",
                            "smaller" + ALBUM_ART_FILENAME])
            subprocess.run(["mv", "smaller" + ALBUM_ART_FILENAME, album_art_gen.ALBUM_ART_PATH])

            LOG.info("Retrying tweet.")

        LOG.info("Sending out album art.")
        api.send_with_one_media(TWEET_TEXT.format(id), album_art_gen.ALBUM_ART_PATH)

        LOG.info(f"Sleeping for {DELAY} seconds.")
        time.sleep(DELAY)
