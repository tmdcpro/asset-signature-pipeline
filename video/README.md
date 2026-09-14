# Walkthrough Video

`asset_signature_pipeline_demo.mp4` is a narrated screencast explaining and
demonstrating `signature_pipeline.py` — how it's structured, what each metric
layer computes, and a live run against a real basket of assets.

It's built as a "captured" production rather than AI-generated video, since the
goal was to accurately show real code and real terminal output:

1. **`narration/*.txt`** — the voiceover script, split into one file per segment
2. **`gen_slides.py`** — generates syntax-highlighted HTML slides (code panels
   + a terminal-output panel) into `slides/*.html`
3. **`slides/*.html`** — the rendered HTML slide sources
4. **`frames/*.png`** — each slide captured as a 1920x1080 PNG
5. **`audio/*.mp3`** — TTS voiceover generated per narration segment
6. **`build_video.py`** — pads each audio segment, turns each frame into a
   matching-length video clip, concatenates everything, and muxes the final
   narration track with fade in/out

## Regenerating

```bash
python3 gen_slides.py      # rebuilds slides/*.html from the pipeline code
# render slides/*.html to frames/*.png at 1920x1080 (any headless browser works)
python3 build_video.py     # assembles frames + audio into the final mp4
```
