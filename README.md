---
age: 6+
players: 2-10
duration: 30 - 90 min
---

# Google Photos Rummy

> Create your own card game for an individual end-of-the-year review based on your Google Photos gallery.

## Goal of the Game

Every year you take hundreds or even thousands of beautiful and funny photos that are linked to wonderful memories.
While you can preserve all of these photos in your personal [Google Photos gallery](https://photos.google.com/) for (almost) ever, keeping these memories actually alive is harder if you do not talk about them with your friends and family.

On New Year's Eve, you usually sit together with (some of) your friends or family members, but the temptation is great to waste your time by drinking too much or watching a political end-of-the-year review on TV only (or if you live in Germany, most likely [Dinner for One](https://www.youtube.com/watch?v=UmsKkebN2O4)).

Why not create your very own end-of-the-year review instead and revive the memories of your most wonderful moments together?
And because just watching photos in a group very quickly gets boring, why not make it a fun party game?
*Google Photos Rummy* (not by Google) is a small card game inspired by [Rummy](https://en.wikipedia.org/wiki/Rummy) and [Rummikub](https://en.wikipedia.org/wiki/Rummikub) that allows you to do right this!

The script from this repository will scrape all photos from your Google Photos Gallery for one year, select a random subset from them, and download it.
Just install & run the script, print out the photos, and reminisce together!

## Preparation of the Game

1. **Clone the repository:**

   ```sh
   git clone https://github.com/LinqLover/google-photos-rummy.git
   cd google-photos-rummy
   ```

2. **Install requirements (Python 3 required, tested with 3.9):**

   ```sh
   pip3 install -r requirements.txt
   ```

3. **Set up credentials for the [Google Photos API](https://developers.google.com/photos):**

   1. Open the [Google Cloud Platform](https://console.cloud.google.com/).
   2. [Create](https://console.cloud.google.com/projectcreate) a new project (suggested name: `GPhotos Rummy`).
   3. Make sure the project is selected and enable the Google Photos API:
      1. [APIs & Services](https://console.cloud.google.com/apis/dashboard)
      2. [Library](https://console.cloud.google.com/apis/library)
      3. [Photos Library API](https://console.cloud.google.com/apis/library/photoslibrary.googleapis.com)
      4. Activate.
   4. [Configure consent screen](https://console.cloud.google.com/apis/credentials/consent) for your project:
      - User type: external
      - App name: `GPhotos Rummy` (suggested, must not contain "Google")
      - Provide e-mail addresses as required.
      - Add scope: `https://www.googleapis.com/auth/photoslibrary.readonly`
      - Add test user: Enter the Gmail address of your Google Photos account here.
   5. Create [credentials](https://console.cloud.google.com/apis/api/photoslibrary.googleapis.com/credentials) for your project:
      1. Create credentials > [OAuth client ID](https://console.cloud.google.com/apis/credentials/oauthclient?previousPage=%2Fapis%2Fapi%2Fphotoslibrary.googleapis.com%2Fcredentials).
	  2. Application type: Desktop app (application name does not matter).
	  3. In the confirmation window, download the credentials file by clicking "Download JSON".
	  4. Save the file as `client_secret.json` into the cloned project folder.

4. **Execute the script to randomly select & download your photos:**

   ```shell
   python3 google_photos_rummy.py
   ```

   The recommended sample size is ~50, depending on the number of memories, players, and available time.

   The script will ask you to perform a few simple steps for authorization.
   Do as instructed.

   Be patient for a few minutes (depending on the number of your photos), a random subset of your photos will be downloaded into the `photos` directory of the project folder.

5. **Print out the downloaded photos (recommended size: 4 images per page) and cut up the pages.**

   > [!TIP]
   > If you use photo paper, you can also use the photos to arrange a nice photo wall after playing the game.

   > [!TIP]
   > Turn the papers over during cutting to avoid self-spoilering!

   For instance, on Windows, you can do this by selecting and right-clicking the downloaded files in the explorer, choosing "Print", and choosing an appropriate page layout on the right:

   <p float="center">
     <img src="https://user-images.githubusercontent.com/38782922/147887994-e7182573-9eb4-4f37-acd7-2ee0779fbc85.png" width="45%" />
     <img src="https://user-images.githubusercontent.com/38782922/147888018-de8073a7-7b5b-41dd-aa67-3926d1b5ac14.png" width="45%" />
  </p>

6. **Mix the printed photos and put them face down in a pile.**

## Play of the Game

If you have ever played [Rummikub](https://en.wikipedia.org/wiki/Rummikub) before, the following will sound familiar to you:
Every player picks up a few photo cards (recommendation: 5 cards) initially.
The players try in turn to lay out a group of at least three cards that must have a connecting element (e.g., a certain place, activity, or event).
Whenever a card is laid out, the players try to remember where the photo was taken and what they did enjoy most on this day.
Be prepared for discussing valid connecting elements during the game, and beware of not allowing for too generic categories!

If the player in turn cannot lay out a group, this player picks up another card instead.
After a player has laid out their first group, the game becomes even more interesting for this player:
They can now modify the existing arrangements by appending cards to existing or rearranging them in new groups on the playfield, with the requirement of maintaining the following invariants:

- Every card group consists of at least 3 and at most 5 (recommended) cards that have one connecting element in common.
- The player must not pick up a card again that has been laid out in an earlier turn.

If a player has laid out all cards in their hand, this player wins.
However, the game may be continued at will so that you do not miss any memory.

**Goal of the game** is to revive as many beautiful moments as possible, not being the first one to win, so don't you dare to plan any tactical maneuvers!

## Addendum

The rules are not strict by any means and may be adjusted, the main goal is to have fun and beautiful memories together.
I tried this out once in a group with 5 people and it worked pretty well, but there is surely room for improvement.
See also the [issues](https://github.com/LinqLover/google-photos-rummy/issues) page for more ideas.
Any feedback and pull requests will be welcome!

Have a nice evening, a happy new year, and be sure to enjoy your life.
