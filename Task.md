# Video Parser

There is a website where videos are uploaded every 2–3 hours. I need to write a bot that will parse new videos and upload them to my Telegram channel.

## Element search:
1. On the main page, find the **ul.videos_ul** element — this is the container that holds the video items.
2. Inside this container, find the video element **li.video_block**. It also has an **id**, you can store the **ID** of the last downloaded video to avoid downloading the same video twice.
3. Inside the video element, find a.image and follow the link from its **href** attribute.
4. On the video page, find the video element by its nesting: **div.col_video** → **div.player-wrapper** → **video**. From the **video** tag, take the **src** attribute and download the video.

## Problems that need to be solved:
1. There is a nuance: the videos are large in size because their duration is 10–30 minutes, and due to this Telegram prohibits bots from uploading videos larger than 50 MB.
2. The video cannot be compressed; it must remain intact and in good quality.