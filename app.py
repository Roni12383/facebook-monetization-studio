import streamlit as st
# --- FIX 1: Patch for ANTIALIAS error ---
import PIL.Image
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS

import requests, os, tempfile, random, zipfile, time
from io import BytesIO
from PIL import Image
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips
from gtts import gTTS

st.set_page_config(page_title="FB Batch Studio - Fixed", layout="wide")
st.title("📘 Facebook Batch Studio - Fixed ✅")
st.write("ANTIALIAS bug fixed + Auto retry")

topics_text = st.text_area("Enter 7 Topics (1 per line):", 
"""How Sokoto farmers turned desert to green farm in 2 years
Katsina woman makes 500k from small garden - her secret
Before and After: This Borno land was dead, now it feeds 100 people
Great Green Wall Nigeria - real footage no one shows you
This simple planting method doubles harvest in Kano
ACReSAL project is changing Northern Nigeria - see proof
Hausa farmer shares 3 secrets to grow food without rain""", height=180)

topics = [t.strip() for t in topics_text.split("\n") if t.strip()][:7]
hook = st.text_input("Hook", "Wait till you see what happened in Sokoto... 😱")

def get_image_with_retry(prompt, width=720, height=1280, retries=3):
    for attempt in range(retries):
        try:
            url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(prompt)}?width={width}&height={height}&nologo=true&seed={random.randint(1,99999)}"
            r = requests.get(url, timeout=45)
            if r.status_code == 200 and len(r.content) > 5000:
                img = Image.open(BytesIO(r.content))
                img.verify() # check if valid
                img = Image.open(BytesIO(r.content)) # reopen after verify
                return img
        except Exception as e:
            time.sleep(2)
    return None

if st.button(f"🚀 GENERATE {len(topics)} VIDEOS"):
    zip_path = os.path.join(tempfile.gettempdir(), "FB_7days.zip")
    
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        overall = st.progress(0)
        success_count = 0
        
        for idx, topic in enumerate(topics):
            st.write(f"### Day {idx+1}: {topic}")
            clips = []
            width, height = 720, 1280
            
            for s in range(3):
                st.write(f"Generating scene {s+1}/3...")
                prompt = f"{topic}, Nigerian farm, ultra realistic, cinematic, Arewa, green land"
                img = get_image_with_retry(prompt, width, height)
                
                if img is None:
                    st.warning(f"Scene {s+1} image failed, skipping")
                    continue

                try:
                    img_path = os.path.join(tempfile.gettempdir(), f"batch_{idx}_{s}.jpg")
                    img.convert("RGB").save(img_path, "JPEG")

                    voice_text = f"{hook}. {topic}." if s==0 else f"Part {s+1}. {topic}"
                    tts = gTTS(text=voice_text[:350], lang='en', slow=False)
                    audio_path = os.path.join(tempfile.gettempdir(), f"batch_{idx}_{s}.mp3")
                    tts.save(audio_path)
                    
                    audio = AudioFileClip(audio_path)
                    clip = ImageClip(img_path, duration=audio.duration + 0.5).set_audio(audio)
                    clip = clip.resize((width, height))
                    clips.append(clip)
                    st.success(f"Scene {s+1} OK")
                    
                except Exception as e:
                    st.error(f"Scene {s+1} error: {e}")

            if clips:
                try:
                    final = concatenate_videoclips(clips, method="compose")
                    out_path = os.path.join(tempfile.gettempdir(), f"Day{idx+1}.mp4")
                    final.write_videofile(out_path, fps=24, codec='libx264', audio_codec='aac', logger=None, threads=1)
                    
                    zipf.write(out_path, f"Day{idx+1}_FB_Reel.mp4")
                    caption = f"{hook}\n\n{topic}\n\n#Nigeria #Arewa #Farming #EcoplotAI"
                    zipf.writestr(f"Day{idx+1}_caption.txt", caption)
                    
                    st.video(out_path)
                    success_count += 1
                    for c in clips:
                        c.close()
                except Exception as e:
                    st.error(f"Stitching failed: {e}")
            
            overall.progress((idx+1)/len(topics))
    
    if success_count > 0:
        st.balloons()
        st.success(f"✅ {success_count} VIDEOS READY!")
        with open(zip_path, "rb") as f:
            st.download_button(f"⬇️ DOWNLOAD {success_count} VIDEOS ZIP", f, "Facebook_7Days.zip", "application/zip")
    else:
        st.error("Still 0 videos. Try 1 topic only for test.")

# --- ALSO UPDATE requirements.txt TO THIS ---
# st.caption("Update requirements.txt to:")
