from datetime import date
import re
import time
import asyncio
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
import pandas as pd
from dotenv import load_dotenv
import os
import requests

from termcolor import colored

from senderMail import send_mail
load_dotenv()

data = date.today()
format_data = data.strftime('%d/%m/%Y')
date_today = str(date.today())
directory = "C:/Users/wilk.silva/Documents/Automation/auto_recarga/Arquivos/download"+date_today+".zip"

planilha = pd.read_excel("arquivos/Relatório Lista cartão PSG atualizado.xlsx",
                         usecols=['Nº Cartão', 'Valor'], dtype={'Nº Cartão': str, 'Valor': float}, skiprows=2, decimal=',')


data_liberacao = input(colored("\n\nInsira a data da liberação: ", "green"))
data_vencimento = input(colored("\n\nInsira a data do vencimento:", "green"))


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
        valor = str(value).replace('.', '')
        if len(valor) < 5:
            v_last = str(valor)+"0"
        else:
            v_last = str(valor)
        v = v_last[0:3] + ","+v_last[3:]

        print(v)
        # if v_last ==
        await new_frame.locator("#txtCard").fill('')
        await new_frame.locator("#txtCard").fill(str(card_number))
        # time.sleep(0.7)
        await new_frame.locator("#query").click()
        # await new_frame.locator("//*[@id='dgdUsuarios']/tbody/tr[2]/td[6]/input").fill('')
        await new_frame.locator("//*[@id='dgdUsuarios']/tbody/tr[2]/td[6]/input").fill(str(v))
        # time.sleep(0.7)
        print(index, card_number, " -> ", v)
    await new_frame.locator("#btnNext").click()
    await new_frame.locator("#txtMemoDate").fill(data_liberacao)
    await new_frame.locator("#txtVctoDate").fill(data_vencimento)
    await new_frame.locator("#btnConfirm").click()
    time.sleep(1)
    await new_frame.locator("//*[@id='btnConfirm']").click()
    frame_alert = page.frame_locator(
        "//*[@id='div_alert']/div[2]/iframe")
    await frame_alert.locator("//*[@id='form1']/div[3]/table/tbody/tr[3]/td/input").click()
    await page.locator("//*[@id='XmlMenu1__ctl87']/td/a").click()
    # new_frame = page.frame_locator("#FRAME")
    time.sleep(1)
    await new_frame.locator("#txtStartDate").fill(date_today)
    await new_frame.locator("#txtEndDate").fill(date_today)
    await new_frame.locator("#query").click()
    # new_context = await browser.new_context()
    time.sleep(1)
    url = await new_frame.locator("//*[@id='dgdOrder']/tbody/tr[2]/td[6]").inner_html()
    # soup = BeautifulSoup(url, 'html.parser')
    # value = soup.find_all('a')
    pvdrId = re.search(r'\d{4},', url).group(0)
    transId = re.search(r',\d{3},', url).group(0)
    seqId = re.search(r',\d{1}\)', url).group(0)
    seqId_rpl = seqId.replace(")", "")
    url_from_boleto = 'https://vtclient.cuiaba.prodatamobility.com.br/Pages/wfm_Billet.aspx?ProviderID=' + \
        pvdrId.replace(",", "")+'&TransactionID='+transId.replace(",",
                                                                  "")+'&SequenceID='+seqId_rpl.replace(",", "")+'.pdf'
    # https://vtclient.cuiaba.prodatamobility.com.br/Pages/wfm_Billet.aspx?ProviderID=3566&TransactionID=512&SequenceID=1
    # page_boleto = await context.new_page()
    print(url_from_boleto)
    await new_frame.locator("//*[@id='dgdOrder']/tbody/tr[2]/td[6]/a/img").click()

    # await page_boleto.goto(url_from_boleto)
    path = "/Arquivos"
    download = requests.get(url_from_boleto)
    arquivo_path = os.path.join(path, os.path.basename(url_from_boleto))
    time.sleep(5)
    with open(arquivo_path, 'wb') as f:
        f.write(download.content)

    # async with page.expect_download() as download_info:
    # await page_boleto.keyboard.press("Control+s")
    # await page_boleto.keyboard.press("Enter")
    # download = await download_info.value

    # download.save_as("/Arquivos/file.pdf")
    # async def handle_download(download):
    #     print(await download.path())
    # page_boleto.on("download", handle_download)
    # await page_boleto.locator("/html/body/pdf-viewer//viewer-toolbar//div/div[3]/cr-icon-button[1]//div/iron-icon").click()
    # async with page_boleto.expect_download() as download_info:
    # download = await download_info.value
    # # await new_page.wait_for_load_state()

    # await download.save_as("/Arquivos/file.pdf").click()
    # await new_page.locator("//*[@id='icon']/iron-icon").click()

    # # await new_page.locator("//*[@id='print']").click()
    # print(len(browser.contexts()))///*[@id="dgdOrder"]/tbody/tr[2]/td[6]

    # await send_mail(date_today, directory)
    time.sleep(60)
    await browser.close()


async def main():
    async with async_playwright() as playwright:
        await run(playwright)
asyncio.run(main())
