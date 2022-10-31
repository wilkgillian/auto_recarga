from datetime import date
import time
import asyncio
from playwright.async_api import async_playwright
import pandas as pd
from dotenv import load_dotenv
import os
load_dotenv()

data = date.today()
format_data = data.strftime('%d/%m/%Y')
planilha = pd.read_excel("arquivos/Relatório Lista cartão PSG.xlsx",
                         usecols=['Nº Cartão', 'Valor'], dtype={'Nº Cartão': str, 'Valor': str}, skiprows=2)

async def run(playwright):
    chromium = playwright.chromium
    browser = await chromium.launch(timeout=10000, headless=False)
    context = await browser.new_context()
    page = await context.new_page()
    await page.goto(os.environ['PAGE'])

    await page.locator("#txtDocNumber").fill(os.environ["LOGIN"])
    await page.locator("#txtSenha").fill(os.environ["PASSWORD"])
    await page.locator("#loginbutton").click()

    await page.locator("#XmlMenu1__ctl76").click()
    await page.locator("//*[@id='XmlMenu1__ctl83']/td/a").click()
    new_frame = page.frame_locator("#FRAME")
    select = new_frame.locator("//*[@id='cboPedType']")
    select.select_option('Valor por usuário')
    await new_frame.locator("#btnNext").click()
    await new_frame.locator("//*[@id='content_visible']/a/img").click()
    for index, row in planilha.iterrows():
        card_number = row['Nº Cartão']
        value = row['Valor']
        valor = str(value).replace('.', ',')
        await new_frame.locator("#txtCard").fill('')
        await new_frame.locator("#txtCard").fill(str(card_number))
        time.sleep(0.7)
        await new_frame.locator("#query").click()
        await new_frame.locator("//*[@id='dgdUsuarios']/tbody/tr[2]/td[6]/input").fill('')
        await new_frame.locator("//*[@id='dgdUsuarios']/tbody/tr[2]/td[6]/input").fill(valor)
        time.sleep(0.7)
        print(index, card_number, " -> ", valor)
    await new_frame.locator("#btnNext").click()
    await new_frame.locator("#txtMemoDate").fill(format_data)
    await new_frame.locator("#txtVctoDate").fill(format_data)
    await new_frame.locator("#btnConfirm").click()

    time.sleep(10)
    await browser.close()


async def main():
    async with async_playwright() as playwright:
        await run(playwright)
asyncio.run(main())
