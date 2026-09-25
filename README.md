# Lunavault

A single self-contained page — no build step, no server, no API keys.

## Deploy on GitHub Pages
1. Create a repo and add `index.html` to it (keep the filename `index.html` so it loads at the root).
2. Settings → Pages → deploy from the branch your file is on.
3. Done — open the published URL.

You can also just double-click `index.html` to run it locally.

## What's inside
- **Cinematic intro** — plays in full on every visit (there's a "Skip intro" button for when you don't want to wait). No video file is used anywhere, so nothing to go missing if you rename or move things — it's all drawn live with canvas.
- **Cursor-reactive moon** — top right, always on screen. Move your mouse left/right anywhere on the page and it sweeps through moon phases in real time. The same moon "is" the intro moon — it docks into the corner once the intro ends.
- **The Vault** — paste a link from any platform (Instagram, Reddit, TikTok, X, Pinterest, YouTube, Facebook, Threads, Snapchat, LinkedIn, Tumblr, Vimeo, or anything else) and Lunavault detects the platform from the URL and guesses whether it's a post or a story, filing it into a matching collection automatically. A platform's folder only appears once you've actually saved something from it.
- Search, filter by platform/type, sort, tag, favorite, export to JSON, and clear the whole vault — all stored locally in your browser (`localStorage`), nothing is sent anywhere.

## Notes
- Everything lives in your browser's local storage. Clearing site data / browsing in a different browser means a fresh, empty vault.
- The platform/type detection is a best guess based on the URL shape — you can override "Post" vs "Story" with the toggle before saving.
