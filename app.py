import streamlit as st
import PIL.Image
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS

import requests, os, tempfile, random, asyncio
from io import BytesIO
from PIL import Image
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips
import edge_tts

st.set_page_config(page_title="FB Flooding Story", layout="wide")
st.title("✅ FIXED VERSION - Flooding Story")

async def make_naija_voice(text, out_path, voice="en-NG-EzinneNeural"):
    comm = edge_tts.Communicate(text, voice, rate="-5%")
    await comm.save(out_path)

def make_voice_safe(text, out_path, voice):
    # FIX for asyncio.run error
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(make_naija_voice(text, out_path, voice))
        loop.close()
    except Exception as e:
        st.error(f"Voice error: {e}")
        raise

def get_image(prompt):
    for _ in range(4):
        try:
            url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(prompt)}?width=720&height=1280&seed={random.randint(1,999999)}&nologo=true"
            r = requests.get(url, timeout=90)
            if r.status_code == 200 and len(r.content) > 15000:
                return Image.open(BytesIO(r.content))
        except:
            continue
    return None

def build_story(topic, location):
    return [
        f"Ku jira ku ga abin da ya faru a {location}. {topic}. My people, kalli har karshe.",
        f"A {location}, mutane suna zubar da shara a cikin magudanun ruwa. For years, gutter don block.",
        f"Shara ta toshe hanya. Ruwa ya kasa wucewa - Water no see road to pass again.",
        f"Can {location}, karamin ruwa ya sa ambaliya ta shiga gida da titi. Flood enter everywhere.",
        f"Al'umma sun tashi, sun share magudanun. Community clear gutter, sun hana zubar da shara.",
        f"Yanzu a {location}, ruwa na tafiya da kyau, ambaliya ta daina. Keep our gutter clean, mu kau da ambaliya. Follow for more, ku biyo mu."
    ]

topic = st.text_input("Topic", "Flooding caused by dumping refuse in waterways")
location = st.text_input("Location", "Sokoto")
voice_opt = st.selectbox("Voice", ["en-NG-EzinneNeural", "en-NG-AbeoNeural"])

if st.button("🎬 GENERATE 3-MIN FLOODING VIDEO"):
    scripts = build_story(topic, location)
    clips = []
    progress = st.progress(0)

    for i in range(6):
        st.write(f"--- Scene {i+1}/6 ---")
        audio_path = os.path.join(tempfile.gettempdir(), f"stable_audio_{i}.mp3")
        img_path = os.path.join(tempfile.gettempdir(), f"stable_img_{i}.jpg")

        try:
            # 1. Audio
            make_voice_safe(scripts[i], audio_path, voice_opt)
            audio = AudioFileClip(audio_path)

            # 2. Image
            scene_types = [
                "blocked gutter filled with plastic refuse Nigeria",
                "people dumping refuse in waterway",
                "blocked drainage dirty water",
                "flooded street houses Nigeria rain",
                "community youths cleaning gutter",
                "clean flowing waterway after cleaning"
            ]
            prompt = f"{location} Nigeria, {scene_types[i]}, ultra realistic, cinematic documentary, 8k, heavy rain"
            img = get_image(prompt) or get_image(f"Nigeria {scene_types[i]}")

            if img:
                img.convert("RGB").save(img_path, "JPEG")

                # FIXED ZOOM - real drone motion
                def resizing(t):
                    return 1 + 0.15 * (t / audio.duration)

                clip = ImageClip(img_path, duration=audio.duration)
                clip = clip.resize(resizing) # only one resize, with time
                clip = clip.set_audio(audio)
                clip = clip.set_position(('center','center')).crop(width=720, height=1280, x_center=clip.w/2, y_center=clip.h/2)
                clips.append(clip)
                st.success(f"Scene {i+1} DONE - {audio.duration:.1f}s")
                audio.close()
            else:
                st.error(f"Scene {i+1} image failed")

        except Exception as e:
            st.error(f"Scene {i+1} error: {e}")
            import traceback; st.code(traceback.format_exc())

        progress.progress((i+1)/6)

    if len(clips) >= 5:
        st.write("Stitching final video...")
        final = concatenate_videoclips(clips, method="compose")
        out_path = os.path.join(tempfile.gettempdir(), "FLOODING_STORY.mp4")
        final.write_videofile(out_path, fps=24, codec='libx264', audio_codec='aac', threads=2)

        st.balloons()
        st.success(f"✅ SUCCESS! {len(clips)}/6 SCENES - {final.duration:.0f}s")
        st.video(out_path)
        with open(out_path, "rb") as f:
            st.download_button("⬇ DOWNLOAD VIDEO", f, f"{location}_flooding.mp4", "video/mp4")

        for c in clips: c.close()
        final.close()
    else:
        st.error(f"Only {len(clips)}/6 made. Try again.")
