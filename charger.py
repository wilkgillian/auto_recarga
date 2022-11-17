from datetime import date
import re
import time
import asyncio
from playwright.async_api import async_playwright
import pandas as pd
from dotenv import load_dotenv
import os

from termcolor import colored

from utils.senderMail import send_mail
load_dotenv()

data = date.today()
format_data = data.strftime('%d/%m/%Y')
date_today = str(date.today())
directory = "C:/Users/wilk.silva/Documents/Automation/auto_recarga/Arquivos/download"+date_today+".zip"

planilha = pd.read_excel("arquivos/Relatório Lista cartão PSG atualizado.xlsx",
                         usecols=['Nº Cartão', 'Valor'], dtype={'Nº Cartão': str, 'Valor': float}, skiprows=2, decimal=',')


data_liberacao = input(
    "Insira a data da liberação no formato: dd/mm/aaaa\n-> ")
data_vencimento = input(
    "Insira a data do vencimento no formato: dd/mm/aaaa\n->")

path = "Arquivos/boleto"+date_today+".png"


async def run(playwright):
    chromium = playwright.chromium
    browser = await chromium.launch(timeout=10000, headless=False)
    context = await browser.new_context()
    page = await context.new_page()
    await page.goto(os.environ['PAGE'])
    try:
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
            await new_frame.locator("#txtCard").fill('')
            await new_frame.locator("#txtCard").fill(str(card_number))
            time.sleep(0.7)
            await new_frame.locator("#query").click()
            time.sleep(0.7)
            await new_frame.locator("//*[@id='dgdUsuarios']/tbody/tr[2]/td[6]/input").fill('')
            await new_frame.locator("//*[@id='dgdUsuarios']/tbody/tr[2]/td[6]/input").fill(str(v))
            time.sleep(0.7)
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
        time.sleep(1)
        await new_frame.locator("#txtStartDate").fill(date_today)
        await new_frame.locator("#txtEndDate").fill(date_today)
        await new_frame.locator("#query").click()
        time.sleep(1)
        url = await new_frame.locator("//*[@id='dgdOrder']/tbody/tr[2]/td[6]").inner_html()
        pvdrId = re.search(r'\d{4},', url).group(0)
        transId = re.search(r',\d{3},', url).group(0)
        seqId = re.search(r',\d{1}\)', url).group(0)
        seqId_rpl = seqId.replace(")", "")
        url_from_boleto = 'https://vtclient.cuiaba.prodatamobility.com.br/Pages/wfm_Billet.aspx?ProviderID=' + \
            pvdrId.replace(",", "")+'&TransactionID='+transId.replace(",",
                                                                      "")+'&SequenceID='+seqId_rpl.replace(",", "")+''
        print(url_from_boleto)
        await new_frame.locator("//*[@id='dgdOrder']/tbody/tr[2]/td[6]/a/img").click()

        page_boleto = await context.new_page()
        await page_boleto.goto(url_from_boleto)
        await page_boleto.wait_for_load_state()
        time.sleep(3)
        await page_boleto.screenshot(path=path, full_page=True)
        pass
    except:
        print(colored("Falha ao recarregar", "red", attrs=["reverse"]))
        return

    try:
        await send_mail(date_today, path)
        pass
    except:
        print(colored("Falha ao enviar e-mail", "red", attrs=["reverse"]))
        return
    await browser.close()
print(colored("Finalizado", "green", attrs=["reverse"]))

async def main():
    async with async_playwright() as playwright:
        await run(playwright)
asyncio.run(main())
