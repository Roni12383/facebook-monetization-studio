import streamlit as st, requests, os, tempfile, random, zipfile
from PIL import Image
from io import BytesIO
from moviepy.editor import ImageClip, AudioFileClip, TextClip, CompositeVideoClip, concatenate_videoclips
from gtts import gTTS

st.set_page_config(page_title="FB Batch Studio - 7 Days", layout="wide")
st.title("📘 Facebook Batch Studio - 7 Reels in 1 Click")
st.write("Generate 1 week of monetizable Reels. For EcoplotAI page.")

# --- BATCH TOPICS ---
st.subheader("Step 1: Enter 7 Topics (1 per line)")
default_topics = """How Sokoto farmers turned desert to green farm in 2 years
Katsina woman makes 500k from small garden - her secret
Before and After: This Borno land was dead, now it feeds 100 people
Great Green Wall Nigeria - real footage no one shows you
This simple planting method doubles harvest in Kano
ACReSAL project is changing Northern Nigeria - see proof
Hausa farmer shares 3 secrets to grow food without rain"""

topics_text = st.text_area("7 Topics:", default_topics, height=200)
topics = [t.strip() for t in topics_text.split("\n") if t.strip()][:7]

hook_style = st.selectbox("Hook Style", ["Wait till you see... 😱", "Nobody told you this...", "This changed everything in Arewa..."])
lang = st.radio("Format", ["Reels 9:16 (90 sec) - RECOMMENDED", "Long 8 min"])

if st.button(f"🚀 GENERATE {len(topics)} VIDEOS - BATCH"):
    if len(topics) < 1:
        st.error("Add at least 1 topic")
        st.stop()

    zip_path = os.path.join(tempfile.gettempdir(), "FB_7days.zip")
    all_videos = []
    
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        overall = st.progress(0)
        
        for idx, topic in enumerate(topics):
            st.write(f"---\n### 🎬 Day {idx+1}: {topic}")
            p_bar = st.progress(0)
            
            is_reel = "Reels" in lang
            width, height = (720,1280) if is_reel else (1280,720)
            num_scenes = 3 if is_reel else 6
            clips = []

            for s in range(num_scenes):
                prompt = f"{topic}, Nigerian farm, ultra realistic, cinematic, emotional, Arewa, {random.randint(1,1000)}"
                url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(prompt)}?width={width}&height={height}"
                try:
                    r = requests.get(url, timeout=25)
                    img = Image.open(BytesIO(r.content))
                    img_path = os.path.join(tempfile.gettempdir(), f"batch_{idx}_{s}.jpg")
                    img.save(img_path)

                    voice_text = f"{hook_style} {topic}" if s==0 else f"Part {s+1}. {topic}"
                    tts = gTTS(text=voice_text, lang='en', slow=False)
                    audio_path = os.path.join(tempfile.gettempdir(), f"batch_{idx}_{s}.mp3")
                    tts.save(audio_path)
                    audio = AudioFileClip(audio_path)
                    
                    clip = ImageClip(img_path, duration=max(30, int(audio.duration))).set_audio(audio).resize((width,height))
                    clip = clip.resize(lambda t: 1 + 0.02*t)
                    
                    if s==0:
                        txt = TextClip(f"DAY {idx+1}: {hook_style}", fontsize=45, color='white', stroke_color='black', stroke_width=2, method='caption', size=(width*0.9, None))
                        txt = txt.set_duration(clip.duration).set_position(('center', height*0.75))
                        clip = CompositeVideoClip([clip, txt])
                    
                    clips.append(clip)
                except Exception as e:
                    st.warning(f"Scene {s+1} failed: {e}")
                p_bar.progress((s+1)/num_scenes)

            if clips:
                final = concatenate_videoclips(clips, method="compose")
                out_path = os.path.join(tempfile.gettempdir(), f"Day{idx+1}_{topic[:20]}.mp4")
                final.write_videofile(out_path, fps=24, codec='libx264', audio_codec='aac', logger=None)
                
                # Add to zip
                zipf.write(out_path, f"Day{idx+1}_FB_Reel.mp4")
                
                # Also save caption
                caption = f"{hook_style}\n\n{topic}\n\nFollow Green Nigeria Stories for more 🇳🇬\n\n#Nigeria #Arewa #Viral #Farming #EcoplotAI #Sokoto #Kano #Borno"
                zipf.writestr(f"Day{idx+1}_caption.txt", caption)
                
                st.video(out_path)
                all_videos.append(out_path)
            
            overall.progress((idx+1)/len(topics))

    st.success(f"✅ {len(all_videos)} VIDEOS READY FOR 7 DAYS!")
    
    with open(zip_path, "rb") as f:
        st.download_button(f"⬇️ DOWNLOAD ALL {len(all_videos)} VIDEOS + CAPTIONS (ZIP)", f, file_name="Facebook_7Days_Batch.zip", mime="application/zip")

st.divider()
st.info("""
**How to use batch for monetization:**

1.  Download ZIP -> You get 7 videos + 7 captions
2.  Go to Meta Business Suite -> Planner -> Schedule 1 Reel per day 8pm WAT
3.  Done. Page runs itself for 1 week.

**Next week:** Change topics, repeat.

This is how faceless pages make $500-$2000/month on Facebook.
""")
