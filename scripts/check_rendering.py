#!/usr/bin/env python3
"""Optional browser QA. Requires Playwright and a local Chromium executable."""
import asyncio
import json
import os
from pathlib import Path
from playwright.async_api import async_playwright

ROOT=Path(__file__).resolve().parents[1]

async def main():
    cases=[('desktop-light',1280,1000,'light'),('desktop-dark',1280,1000,'dark'),
           ('mobile-light',390,1200,'light'),('mobile-dark',390,1200,'dark'),
           ('narrow-light',320,1200,'light'),('tablet-dark',768,1200,'dark')]
    results=[]
    async with async_playwright() as p:
        browser=await p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH','/usr/bin/chromium'),
            headless=True,args=['--no-sandbox','--allow-file-access-from-files','--disable-background-networking'])
        for name,width,height,theme in cases:
            context=await browser.new_context(viewport={'width':width,'height':height},device_scale_factor=1,color_scheme=theme)
            page=await context.new_page()
            await page.goto((ROOT/'.preview'/f'{theme}.html').as_uri())
            await page.wait_for_function("document.documentElement.dataset.validation !== undefined")
            status=await page.get_attribute('html','data-validation')
            assert status=='passed',await page.locator('body').inner_text()
            result=json.loads(await page.locator('#validation').inner_text())
            assert result['width']==width,result
            assert result['mobile']==(width<=768),result
            await page.locator('main').screenshot(path=str(ROOT/'.preview'/f'final-{name}.png'))
            print('PASS:',name,json.dumps(result))
            results.append({'case':name,**result})
            await context.close()
        await browser.close()
    (ROOT/'.preview/rendering-results.json').write_text(json.dumps(results,indent=2))

if __name__=='__main__':asyncio.run(main())
