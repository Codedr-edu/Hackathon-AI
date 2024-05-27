import asyncio
import playsound
import edge_tts
import os

VOICE = "en-US-AndrewNeural"
OUTPUT_FILE = "test.mp3"


async def amain(TEXT, emotion) -> None:
    """Main function"""
    set_dict = {
        "[happy]": {"rate": "+20%", "pitch": "+20Hz"},
        "[sad]": {"rate": "-10%", "pitch": "-25Hz"},
        "[angry]": {"rate": "+25%", "pitch": "-20Hz"},
        "[scared]": {"rate": "+20%", "pitch": "-10Hz"}
    }
    communicate = edge_tts.Communicate(
        TEXT, VOICE, rate=set_dict[emotion]["rate"], pitch=set_dict[emotion]["pitch"], volume="+170%")
    await communicate.save(OUTPUT_FILE)


def tts_run(Text, emotion):
    asyncio.run(
        amain(Text, "[happy]"))
    audio_file = os.path.dirname(__file__) + '\\test.mp3'
    playsound.playsound(audio_file)
    os.remove(audio_file)
