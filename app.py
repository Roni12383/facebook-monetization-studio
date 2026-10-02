import streamlit as st
import PIL.Image
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS

import requests, os, tempfile, random, asyncio
from io import BytesIO
from PIL import Image, ImageDraw
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips
import edge_tts

st.set_page_config(page_title="Arewa Flooding Story - STABLE", layout="wide")
st.title("✅ AREWA FLOODING STORY - 6/6 MUST PASS")
st.success("Hausa+Pidgin + No Pollinations Fail + No Audio Fail")

# --- VOICE FIX ---
async def make_naija_voice(text, out_path, voice="en-NG-EzinneNeural"):
    comm = edge_tts.Communicate(text, voice, rate="-5%")
    await comm.save(out_path)

def make_voice_safe(text, out_path, voice):
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(make_naija_voice(text, out_path, voice))
        loop.close()
        return True
    except Exception as e:
        st.error(f"Voice error: {e}")
        return False

# --- IMAGE FIX WITH BACKUP ---
def get_image(prompt):
    for _ in range(3):
        try:
            url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(prompt)}?width=720&height=1280&seed={random.randint(1,9999999)}&nologo=true"
            r = requests.get(url, timeout=90)
            if r.status_code == 200 and len(r.content) > 15000:
                return Image.open(BytesIO(r.content))
        except:
            continue
    return None

def create_backup_image(title, scene_num):
    img = Image.new('RGB', (720, 1280), color=(15, 25, 45))
    draw = ImageDraw.Draw(img)
    for y in range(1280):
        r = int(15 + y * 0.06)
        g = int(25 + y * 0.09)
        b = int(70 + y * 0.12)
        draw.line([(0, y), (720, y)], fill=(min(r,90), min(g,110), min(b,180)))
    draw.text((360, 640), f"{title}\nSCENE {scene_num+1}", fill="white", anchor="mm", align="center")
    return img

# --- HAUSA + PIDGIN STORY ---
def build_story(topic, location):
    return [
        f"Ku jira ku ga abin da ya faru a {location}. {topic}. My people, kalli har karshe.",
        f"A {location}, mutane suna zubar da shara a cikin magudanun ruwa. For years, gutter don block.",
        f"Shara ta toshe hanya. Ruwa ya kasa wucewa - Water no see road to pass again.",
        f"Can {location}, karamin ruwa ya sa ambaliya ta shiga gida da titi. Flood enter everywhere.",
        f"Al'umma sun tashi, sun share magudanun. Community clear gutter, sun hana zubar da shara.",
        f"Yanzu a {location}, ruwa na tafiya da kyau, ambaliya ta daina. Keep our gutter clean, mu kau da ambaliya. Follow for more."
    ]

# --- UI ---
topic = st.text_input("Topic", "Flooding caused by dumping refuse in waterways")
location = st.text_input("Location", "Sokoto")
voice_opt = st.selectbox("Voice", ["en-NG-EzinneNeural", "en-NG-AbeoNeural"])

if st.button("🎬 GENERATE 6/6 AREWA VIDEO"):
    scripts = build_story(topic, location)
    # SAFE PROMPTS - No banned words like refuse/waste/dirty/flooded
    scene_types = [
        f"beautiful aerial view {location} northern Nigeria city",
        f"Hausa community street northern Nigeria Arewa",
        f"water drainage channel northern Nigeria after rain",
        f"rainy day in {location} northern Nigeria street",
        f"Hausa youths community working together Arewa unity",
        f"beautiful clean street {location} sunset northern Nigeria"
    ]

    clips = []
    progress = st.progress(0)
    status_text = st.empty()

    for i in range(6):
        status_text.write(f"Processing Scene {i+1}/6: {scene_types[i]}")
        uid = random.randint(10000, 999999)
        audio_path = os.path.join(tempfile.gettempdir(), f"arewa_a_{uid}_{i}.mp3")
        img_path = os.path.join(tempfile.gettempdir(), f"arewa_i_{uid}_{i}.jpg")

        try:
            # AUDIO
            ok = make_voice_safe(scripts[i], audio_path, voice_opt)
            if not ok or not os.path.exists(audio_path) or os.path.getsize(audio_path) < 2000:
                st.warning(f"Scene {i+1} audio retry...")
                make_voice_safe(scripts[i], audio_path, voice_opt)

            audio = AudioFileClip(audio_path)
            if audio.duration < 1:
                raise Exception("Audio too short")

            # IMAGE
            img = get_image(f"{scene_types[i]}, cinematic documentary, ultra realistic, 8k, Arewa")
            if img is None:
                st.warning(f"Scene {i+1} using backup image (Pollinations slow)")
                img = create_backup_image(location, i)

            img.convert("RGB").save(img_path, "JPEG", quality=95)

            # CLIP - SIMPLEST STABLE VERSION
            clip = ImageClip(img_path, duration=audio.duration)
            # Very gentle zoom
            clip = clip.resize(lambda t: 1 + 0.06 * (t / max(audio.duration, 1)))
            clip = clip.set_audio(audio)
            clip = clip.on_color(size=(720, 1280), color=(0,0,0), pos=('center','center'))

            clips.append(clip)
            st.success(f"Scene {i+1} DONE ✅ {audio.duration:.1f}s")

        except Exception as e:
            st.error(f"Scene {i+1} error: {e}")
            try:
                # Last chance backup
                emergency_img = create_backup_image(location, i)
                emergency_img.save(img_path, "JPEG")
                if not os.path.exists(audio_path):
                    make_voice_safe(scripts[i], audio_path, voice_opt)
                audio = AudioFileClip(audio_path)
                clip = ImageClip(img_path, duration=audio.duration).set_audio(audio)
                clip = clip.on_color(size=(720, 1280), color=(0,0,0), pos=('center','center'))
                clips.append(clip)
                st.warning(f"Scene {i+1} recovered with backup ✅")
            except Exception as e2:
                st.error(f"Scene {i+1} failed totally: {e2}")

        progress.progress((i+1)/6)

    status_text.write("Finalizing video...")
    if len(clips) >= 5:
        try:
            final = concatenate_videoclips(clips, method="compose")
            out_path = os.path.join(tempfile.gettempdir(), f"AREWA_FLOODING_{random.randint(1,9999)}.mp4")
            final.write_videofile(out_path, fps=24, codec='libx264', audio_codec='aac', threads=2, logger=None)

            st.balloons()
            st.success(f"✅ SUCCESS! {len(clips)}/6 SCENES - {final.duration:.0f}s - READY FOR FACEBOOK MONETIZATION")
            st.video(out_path)

            with open(out_path, "rb") as f:
                st.download_button(f"⬇ DOWNLOAD {final.duration:.0f}s VIDEO", f, f"{location}_Arewa_Flooding.mp4", "video/mp4")

            for c in clips:
                try: c.close()
                except: pass
            final.close()

        except Exception as e:
            st.error(f"Final stitch error: {e}")
            import traceback
            st.code(traceback.format_exc())
    else:
        st.error(f"Only {len(clips)}/6 made. Click GENERATE again - backup system will complete it.")
