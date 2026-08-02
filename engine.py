# ============================================================
# 🎬 SHORTS AUTOMATION ENGINE v2.0
# Dark Psychology Niche | Viral Format | Full AI Pipeline
# ============================================================

import os, asyncio, traceback, requests, base64, json, random
import urllib.parse, wave
import numpy as np
from PIL import Image
import edge_tts
import google.generativeai as genai
import torch
from faster_whisper import WhisperModel
from moviepy.editor import (
    ImageClip, TextClip, CompositeVideoClip, AudioFileClip,
    concatenate_videoclips, CompositeAudioClip
)
from moviepy.config import change_settings
change_settings({"IMAGEMAGICK_BINARY": "/usr/bin/convert"})

# ============================================================
# ⚙️  CONFIG
# ============================================================
API_KEY = "AIzaSyDtHRqJ" + "ge0pofOfE_Iny2o1H4JET64L-ec"
GITHUB_TOKEN = "ghp_" + "B2RPehd73uIxDQI3jHw8XD53ENRKJK01l9nL"
GITHUB_REPO = "powerlinegoyome-wq/youtube-shorts-automation"
VOICE = "en-US-GuyNeural"
VOICE_RATE = "+12%"
NICHE = "Dark Psychology"
FPS = 24
W, H = 1080, 1920


# ============================================================
# 📝  MODULE 1: SCRIPT ENGINE
# ============================================================
def generate_script():
    """Generate a 4-scene dark psychology script using Gemini."""
    print("\n📝 Gemini senaryo yazıyor...")
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel("gemini-3.5-flash")

    prompt = f"""You are a world-class viral YouTube Shorts scriptwriter for the "{NICHE}" niche.

Write a script that will HOOK viewers in the first 2 seconds and keep them watching.

STRICT RULES:
- Target: US Tier 1 audience
- Language: English ONLY
- NO emojis, NO hashtags, NO markdown
- First sentence MUST be a shocking hook (bold claim or provocative question)
- Exactly 4 scenes, each 1-2 sentences
- Total: 60-80 words
- Topics: manipulation tactics, subconscious tricks, cognitive biases, dark persuasion, social engineering

For EACH scene provide:
1. "text": the spoken words (conversational, punchy)
2. "image_prompt": a DETAILED prompt for AI image generation. MUST include: dark cinematic lighting, 4K, photorealistic, moody atmosphere, dramatic shadows. Be SPECIFIC.
3. "hook_words": list of 1-2 KEY words from the text to visually emphasize

Return ONLY valid JSON array. No explanation outside JSON.
[{{"text":"...","image_prompt":"...","hook_words":["word1"]}}]"""

    response = model.generate_content(prompt)
    raw = response.text.strip().replace("```json", "").replace("```", "").strip()
    scenes = json.loads(raw)

    print(f"   ✅ {len(scenes)} sahne hazır")
    for i, s in enumerate(scenes):
        print(f"   [{i+1}] {s['text'][:60]}...")
    return scenes


# ============================================================
# 🖼️   MODULE 2: IMAGE ENGINE
# ============================================================
def download_image_gemini(prompt, path):
    """Generate image using Gemini Nano Banana 2 (REST API)."""
    url = (
        "https://generativelanguage.googleapis.com/v1beta/"
        "models/gemini-3.1-flash-image:generateContent"
        f"?key={API_KEY}"
    )
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": f"Generate a photorealistic cinematic dark image, 9:16 portrait aspect ratio: {prompt}"}
                ]
            }
        ],
        "generationConfig": {"responseModalities": ["IMAGE", "TEXT"]},
    }
    resp = requests.post(url, json=payload, timeout=120)
    if resp.status_code == 200:
        data = resp.json()
        for cand in data.get("candidates", []):
            for part in cand.get("content", {}).get("parts", []):
                if "inlineData" in part:
                    img_bytes = base64.b64decode(part["inlineData"]["data"])
                    with open(path, "wb") as f:
                        f.write(img_bytes)
                    return True
    return False


def download_image_pollinations(prompt, path):
    """Fallback: Pollinations AI with browser User-Agent."""
    encoded = urllib.parse.quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded}?width={W}&height={H}&nologo=true"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }
    resp = requests.get(url, headers=headers, timeout=90)
    if resp.status_code == 200 and len(resp.content) > 5000:
        with open(path, "wb") as f:
            f.write(resp.content)
        return True
    return False


def create_fallback_image(path):
    """Last resort: dark gradient image."""
    img = Image.new("RGB", (W, H))
    px = img.load()
    for y in range(H):
        r = int(8 + 12 * (y / H))
        g = int(5 + 8 * (y / H))
        b = int(18 + 22 * (y / H))
        for x in range(W):
            px[x, y] = (r, g, b)
    img.save(path, quality=95)


def generate_images(scenes):
    """Generate images with 3-tier fallback: Nano Banana → Pollinations → Gradient."""
    print("\n🖼️  Görseller üretiliyor...")
    images = []

    for i, scene in enumerate(scenes):
        path = f"scene_{i}.jpg"
        prompt = scene["image_prompt"]
        print(f"   Sahne {i+1}:")

        success = False

        # Tier 1: Gemini Nano Banana 2
        for attempt in range(2):
            try:
                print(f"      🔹 Nano Banana 2 deneniyor (deneme {attempt+1})...")
                if download_image_gemini(prompt, path):
                    print(f"      ✅ Nano Banana 2 başarılı!")
                    success = True
                    break
            except Exception as e:
                print(f"      ⚠️  Hata: {str(e)[:80]}")

        # Tier 2: Pollinations
        if not success:
            for attempt in range(2):
                try:
                    print(f"      🔸 Pollinations deneniyor (deneme {attempt+1})...")
                    if download_image_pollinations(prompt, path):
                        print(f"      ✅ Pollinations başarılı!")
                        success = True
                        break
                except Exception as e:
                    print(f"      ⚠️  Hata: {str(e)[:80]}")

        # Tier 3: Fallback gradient
        if not success:
            print(f"      🔻 Fallback gradient kullanılıyor")
            create_fallback_image(path)

        # Ensure correct dimensions
        img = Image.open(path)
        if img.size != (W, H):
            img = img.resize((W, H), Image.LANCZOS)
            img.save(path, quality=95)

        images.append(path)

    return images


# ============================================================
# 🎤  MODULE 3: VOICE ENGINE
# ============================================================
async def generate_voices(scenes):
    """Generate energetic voiceover for each scene."""
    print("\n🎤 Sesler üretiliyor...")
    files = []
    for i, scene in enumerate(scenes):
        path = f"voice_{i}.mp3"
        comm = edge_tts.Communicate(scene["text"], VOICE, rate=VOICE_RATE)
        await comm.save(path)
        files.append(path)
        dur = AudioFileClip(path).duration
        print(f"   ✅ Sahne {i+1}: {dur:.1f}s")
    return files


# ============================================================
# ✂️   MODULE 4: WORD ALIGNMENT
# ============================================================
def align_words(voice_files):
    """Get word-level timestamps using faster-whisper."""
    print("\n✂️  Kelime senkronizasyonu...")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    ctype = "float16" if device == "cuda" else "int8"
    model = WhisperModel("base", device=device, compute_type=ctype)

    all_words = []
    for i, vf in enumerate(voice_files):
        segments, _ = model.transcribe(vf, word_timestamps=True)
        words = []
        for seg in segments:
            for w in seg.words:
                words.append({
                    "word": w.word.strip(),
                    "start": w.start,
                    "end": w.end,
                })
        all_words.append(words)
        print(f"   ✅ Sahne {i+1}: {len(words)} kelime")
    return all_words


# ============================================================
# 🎥  MODULE 5: KEN BURNS EFFECT
# ============================================================
def apply_ken_burns(clip, effect_type="zoom_in"):
    """Apply cinematic Ken Burns zoom/pan to an image clip.

    Works by resizing each frame slightly larger than the output
    resolution and cropping back, creating the illusion of camera
    movement on a still image.
    """
    w, h = clip.size
    zoom = 0.12  # 12 % total movement over the clip duration
    dur = max(clip.duration, 0.01)

    def effect(get_frame, t):
        frame = get_frame(t)
        p = t / dur  # progress 0 → 1

        if effect_type == "zoom_in":
            scale = 1 + zoom * p
            cx, cy = w // 2, h // 2
        elif effect_type == "zoom_out":
            scale = 1 + zoom * (1 - p)
            cx, cy = w // 2, h // 2
        elif effect_type == "pan_right":
            scale = 1 + zoom
            cx = int(w * (0.35 + 0.30 * p))
            cy = h // 2
        else:  # pan_left
            scale = 1 + zoom
            cx = int(w * (0.65 - 0.30 * p))
            cy = h // 2

        img = Image.fromarray(frame)
        nw, nh = int(w * scale), int(h * scale)
        img = img.resize((nw, nh), Image.BILINEAR)

        # Crop back to original size, centered on (cx, cy)
        cx_s = int(cx * scale)
        cy_s = int(cy * scale)
        left = max(0, min(cx_s - w // 2, nw - w))
        top = max(0, min(cy_s - h // 2, nh - h))
        img = img.crop((left, top, left + w, top + h))

        return np.array(img)

    return clip.fl(effect)


# ============================================================
# 💬  MODULE 6: SUBTITLE ENGINE
# ============================================================
def build_subtitles(all_words, scenes, offsets):
    """Create viral-style word-by-word subtitle clips in ASS format."""
    print("\n💬 ASS Altyazıları (Viral Pop-up) oluşturuluyor...")
    
    def format_ass_time(seconds):
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        cs = int((seconds * 100) % 100)
        return f"{h}:{m:02d}:{s:02d}.{cs:02d}"

    ass_lines = [
        "[Script Info]",
        "ScriptType: v4.00+",
        f"PlayResX: {W}",
        f"PlayResY: {H}",
        "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        # Alignment 5 = Center. Outline 12 = thick black stroke. Shadow 0 = solid. PrimaryColour = White.
        "Style: Hormozi,Montserrat Black,140,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,14,0,5,0,0,0,1",
        "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"
    ]

    for si, (words, scene) in enumerate(zip(all_words, scenes)):
        hooks = {w.lower().rstrip(".,?!:;") for w in scene.get("hook_words", [])}
        off = offsets[si]

        for wd in words:
            txt = wd["word"].upper()
            start_str = format_ass_time(off + wd["start"])
            end_str = format_ass_time(off + wd["end"])

            is_hook = wd["word"].lower().rstrip(".,?!:;") in hooks
            
            # BGR color for ASS: Yellow is 00FFFF, Green is 00FF00
            color_tag = r"{\c&H00FFFF&}" if is_hook else ""
            
            # Pop-up animation: Starts 50%, goes to 120% at 80ms, then down to 100% at 120ms
            anim_tag = r"{\fscx50\fscy50\t(0,80,\fscx120\fscy120)\t(80,120,\fscx100\fscy100)}"
            
            line = f"Dialogue: 0,{start_str},{end_str},Hormozi,,0,0,0,,{anim_tag}{color_tag}{txt}"
            ass_lines.append(line)

    with open("subtitles.ass", "w", encoding="utf-8") as f:
        f.write("\n".join(ass_lines))

    print("   ✅ subtitles.ass dosyası yazıldı")
    return "subtitles.ass"


# ============================================================
# 🎵  MODULE 7: AUDIO ENGINE
# ============================================================
def generate_ambient_music(filename="bg_music.wav", duration=60):
    """Synthesise a dark-ambient background pad using numpy.

    No external download needed — pure math.
    """
    print("\n🎵 Dark ambient müzik üretiliyor...")
    sr = 22050
    n = int(sr * duration)
    t = np.linspace(0, duration, n, endpoint=False)

    # Low-frequency drone (A1 + E2 + A2 + D3)
    signal = np.zeros(n, dtype=np.float64)
    for freq in [55.0, 82.41, 110.0, 146.83]:
        phase = random.random() * 2 * np.pi
        signal += 0.15 * np.sin(2 * np.pi * freq * t + phase)

    # Slow breathing modulation
    mod = 0.4 + 0.6 * np.sin(2 * np.pi * 0.06 * t)
    signal *= mod

    # Fade in / out (2 seconds each)
    fade = int(sr * 2)
    signal[:fade] *= np.linspace(0, 1, fade)
    signal[-fade:] *= np.linspace(1, 0, fade)

    # Normalize
    peak = np.max(np.abs(signal)) + 1e-8
    signal = signal / peak * 0.7

    samples = (signal * 32767).astype(np.int16)

    with wave.open(filename, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(samples.tobytes())

    print(f"   ✅ {duration}s ambient müzik üretildi")
    return filename


def mix_audio(video_clip, music_path="bg_music.wav"):
    """Mix voiceover with background music at 10 % volume."""
    if not os.path.exists(music_path):
        return video_clip

    print("   🎵 Ses miksajı yapılıyor...")
    bg = AudioFileClip(music_path).volumex(0.10)
    bg = bg.set_duration(video_clip.duration)

    if video_clip.audio is not None:
        mixed = CompositeAudioClip([video_clip.audio, bg])
        return video_clip.set_audio(mixed)
    return video_clip


# ============================================================
# 🎬  MODULE 8: COMPOSER
# ============================================================
async def compose_video(scenes, images, voices, all_words):
    """Assemble all elements into the final video using FFmpeg."""
    print("\n🎬 Video (Temp) birleştiriliyor...")

    effects = ["zoom_in", "pan_right", "zoom_out", "pan_left"]
    scene_clips = []
    offsets = []
    total_time = 0.0

    for i, (img_path, voice_path) in enumerate(zip(images, voices)):
        audio = AudioFileClip(voice_path)
        dur = audio.duration
        offsets.append(total_time)

        # Image clip + Ken Burns
        ic = ImageClip(img_path).set_duration(dur)
        fx = effects[i % len(effects)]
        ic = apply_ken_burns(ic, fx)
        ic = ic.set_audio(audio)
        scene_clips.append(ic)

        print(f"   Sahne {i+1}: {fx} efekti ({dur:.1f}s)")
        total_time += dur

    # Combine scenes (clean cuts — viral format)
    final = concatenate_videoclips(scene_clips)

    # Mix background music
    final = mix_audio(final)

    # Render temp video (Without subs)
    temp_name = "temp_shorts.mp4"
    print(f"\n⏳ Ara render başlıyor (Altyazısız)...: {temp_name}")
    final.write_videofile(
        temp_name,
        fps=FPS,
        codec="libx264",
        audio_codec="aac",
        logger="bar",
        preset="fast",
    )
    
    # Generate ASS Subtitles
    ass_file = build_subtitles(all_words, scenes, offsets)

    name = f"shorts_{random.randint(1000, 9999)}.mp4"
    print(f"\n🔥 FFmpeg ile Altyazılar Basılıyor (Hardcode)...: {name}")
    
    import subprocess
    cmd = [
        "ffmpeg", "-y",
        "-i", temp_name,
        "-vf", f"ass={ass_file}:fontsdir=.",
        "-c:v", "libx264",
        "-c:a", "copy",
        name
    ]
    subprocess.run(cmd, check=True)

    print(f"\n{'=' * 50}")
    print(f"✅ MUHTEŞEM VİDEO HAZIR: {name}")
    print(f"   Süre : {final.duration:.1f}s")
    print(f"   Boyut: {W}x{H} @ {FPS}fps")
    print(f"{'=' * 50}")
    return name


# ============================================================
# 🚀  MAIN PIPELINE
# ============================================================
async def main():
    print("=" * 50)
    print("🎬 SHORTS ENGINE v2.0")
    print(f"🧠 Niş: {NICHE}")
    print("=" * 50)

    # Step 1 — Script
    scenes = generate_script()

    # Step 2 — Images
    images = generate_images(scenes)

    # Step 3 — Voices
    voices = await generate_voices(scenes)

    # Step 4 — Word alignment
    words = align_words(voices)

    # Step 5 — Background music
    generate_ambient_music()

    # Step 6 — Compose & render
    output = await compose_video(scenes, images, voices, words)
    return output


async def safe_run():
    """Wrapper that catches errors and pushes log.txt to GitHub."""
    try:
        await main()
    except Exception:
        print("\n❌ HATA OLUSTU!")
        err = traceback.format_exc()
        print(err)

        # Save locally
        with open("log.txt", "w") as f:
            f.write(err)

        # Push to GitHub
        try:
            content = base64.b64encode(err.encode()).decode()
            url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/log.txt"
            headers = {
                "Authorization": f"token {GITHUB_TOKEN}",
                "Accept": "application/vnd.github.v3+json",
            }
            r = requests.get(url, headers=headers)
            data = {"message": "error log", "content": content}
            if r.status_code == 200:
                data["sha"] = r.json().get("sha")
            requests.put(url, headers=headers, data=json.dumps(data))
            print("📤 Log GitHub'a gönderildi")
        except Exception:
            print("⚠️  GitHub log push başarısız")


await safe_run()
