# Roku Direct Publisher JSON Generator

The product of this script is JSON sufficient to drive a Roku channel per the specifications here: https://github.com/rokudev/feed-specifications

Serve the JSON on the web from anywhere and point your custom Roku channel at it. Roku will parse and validate the JSON prior to publishing, and just like that, your content is on the channel.

## Usage

First, sign up for an OMDb API key at http://www.omdbapi.com/. This is free, up to 1k calls per day. But throw 'em some cash anyway.

Next, sign up for a Roku developer account at https://developer.roku.com and make a new channel. There are lots of things to configure aside from the requisite JSON, namely several images at very specific
dimensions that will be displayed when navigating through your channel on the Roku. When you set the Direct Publisher JSON URL, the filename there must match the value of JSON_FEED_FILENAME in this script.

Point this script at any folder with movie video that meets the following critera:

* .mp4 or .m4v
* named for the movie with underscores replacing spaces, e.g. 2001_a_space_odyssey.mp4

Files may be in any subdirectory structure.

Change the configuration to match your environment - the files naturally must be served on the public web, so change the base URL appropriately, add your OMDb API key, set the JSON filename as expected
for your channel in your Roku developer account. Maybe even set the timezone if you want to be picky.

Now kick it off and send any bugs right on over to me at <a href="mailto:tim@palkosoftware.com">tim@palkosoftware.com</a>.
