import asyncio,sys
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
        pg=await b.new_page(viewport={'width':1360,'height':820})
        errs=[];pg.on('pageerror',lambda e:errs.append(str(e)));pg.on('console',lambda m:errs.append('console:'+m.text) if m.type=='error' else None)
        await pg.goto('file:///home/claude/mindmapper/index.html');await pg.wait_for_timeout(1200)
        await pg.screenshot(path='shots/1.png')
        await pg.fill('#q','How might we make weekend mornings feel like a mini vacation?')
        for s in ['Breakfast picnic on the balcony','Phone-free first two hours','Neighbourhood walking tour','Cook a dish from a random country','Sunrise swim','Board game brunch']:
            await pg.fill('#seedin',s);await pg.press('#seedin','Enter')
        await pg.screenshot(path='shots/2.png')
        await pg.click('#goBtn');await pg.wait_for_timeout(900)
        await pg.screenshot(path='shots/3.png')
        # select a node, add child
        n=pg.locator('.node.seed').first;await n.click();await pg.wait_for_timeout(200)
        await pg.screenshot(path='shots/4.png')
        await pg.keyboard.press('Tab');await pg.wait_for_timeout(200);await pg.keyboard.type('Bring a hammock');await pg.keyboard.press('Enter')
        await pg.wait_for_timeout(300)
        # drag a node
        bb=await pg.locator('.node.seed').nth(2).bounding_box()
        await pg.mouse.move(bb['x']+30,bb['y']+20);await pg.mouse.down();await pg.mouse.move(bb['x']+130,bb['y']+120,steps=8);await pg.mouse.up()
        await pg.click('#tidy');await pg.wait_for_timeout(2500)
        await pg.screenshot(path='shots/5.png')
        print(errs)
        await b.close()
asyncio.run(main())
