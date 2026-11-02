#!/usr/bin/env python3
"""Optional browser checks for binary rain and reduced-motion fallback."""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright
ROOT=Path(__file__).resolve().parents[1]
async def main():
 async with async_playwright() as p:
  browser=await p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--allow-file-access-from-files'])
  page=await browser.new_page(viewport={'width':1280,'height':1000})
  await page.goto((ROOT/'assets/terminal-desktop.svg').as_uri())
  await page.wait_for_timeout(100)
  selectors=['#matrix-rain .rain-motion > g:first-child','#lens-reflections .rain-motion > g:first-child']
  before=[await page.locator(s).first.evaluate('(el)=>el.getCTM().f') for s in selectors]
  await page.wait_for_timeout(800)
  after=[await page.locator(s).first.evaluate('(el)=>el.getCTM().f') for s in selectors]
  for name,a,b in zip(['background','lenses'],before,after):
   assert abs(b-a)>3,(name,a,b)
   print('PASS animated',name,'vertical movement',round(b-a,1),'px')
  await page.screenshot(path=str(ROOT/'.preview/animated-final.png'))
  await page.emulate_media(reduced_motion='reduce')
  assert await page.locator('#matrix-rain .rain-motion').evaluate('(el)=>getComputedStyle(el).display')=='none'
  assert await page.locator('#matrix-rain .rain-still').evaluate('(el)=>getComputedStyle(el).display')=='inline'
  a=await page.screenshot();await page.wait_for_timeout(300);b=await page.screenshot()
  assert a==b,'Reduced motion still animates visibly'
  print('PASS reduced-motion: static digits replace moving digits; image remains unchanged')
  await browser.close()
asyncio.run(main())
