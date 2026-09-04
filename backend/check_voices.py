import asyncio
import edge_tts

async def main():
    voices = await edge_tts.list_voices()
    indian_locales = ['en-IN', 'hi-IN', 'ta-IN', 'te-IN', 'mr-IN', 'gu-IN', 'kn-IN', 'ml-IN', 'bn-IN', 'ur-IN']
    filtered = [v for v in voices if any(loc in v['Locale'] for loc in indian_locales)]
    for v in filtered:
        print(f"{v['Locale']}: {v['ShortName']} ({v['Gender']})")

if __name__ == "__main__":
    asyncio.run(main())
