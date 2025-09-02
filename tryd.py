import asyncio
from googletrans import Translator
async def translate_text():
    async with Translator() as translator:
        result = await translator.translate('안녕하세요.')
        print(result)  # <Translated src=ko dest=en text=Good evening. pronunciation=Good evening.>
        result = await translator.translate('안녕하세요.', dest='ja')
        print(result)  # <Translated src=ko dest=ja text=こんにちは。 pronunciation=Kon'nichiwa.>
        result = await translator.translate('veritas lux mea', src='la')
        print(result)  # <Translated src=la dest=en text=The truth is my light pronunciation=The truth is my light>
asyncio.run(translate_text())