import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
        pg=await b.new_page(viewport={'width':1360,'height':820})
        errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto('file:///home/claude/mindmapper/index.html');await pg.wait_for_timeout(800)
        await pg.fill('#q','How might we make weekend mornings feel like a mini vacation?')
        for s in ['Breakfast picnic on the balcony','Phone-free first two hours','Neighbourhood walking tour','Cook a dish from a random country','Sunrise swim','Board game brunch']:
            await pg.fill('#seedin',s);await pg.press('#seedin','Enter')
        await pg.click('#goBtn');await pg.wait_for_timeout(900)
        await pg.screenshot(path='shots/6.png')
        # link drag from seed 0 handle to seed 2
        a=pg.locator('.node.seed').nth(0);await a.hover();h=await a.locator('.hd').bounding_box()
        t=await pg.locator('.node.seed').nth(1).bounding_box()
        await pg.mouse.move(h['x']+9,h['y']+9);await pg.mouse.down();await pg.mouse.move(t['x']+t['width']/2,t['y']+t['height']/2,steps=10);await pg.mouse.up()
        await pg.wait_for_timeout(300)
        # drag handle into empty space to create
        a=pg.locator('.node.seed').nth(5);await a.hover();h=await a.locator('.hd').bounding_box()
        await pg.mouse.move(h['x']+9,h['y']+9);await pg.mouse.down();await pg.mouse.move(h['x']-250,h['y']-150,steps=10);await pg.mouse.up()
        await pg.keyboard.type('Pack a thermos');await pg.keyboard.press('Enter');await pg.wait_for_timeout(300)
        await pg.screenshot(path='shots/7.png')
        await pg.click('#tidy');await pg.wait_for_timeout(2500)
        await pg.screenshot(path='shots/8.png')
        g=await pg.evaluate("(()=>{const k=S.edges[0];const gg=edgeGeom(k);return [gg.mx*V.k+V.x,gg.my*V.k+V.y]})()");await pg.mouse.click(g[0],g[1]);await pg.wait_for_timeout(200);await pg.screenshot(path='shots/9.png')
        print(errs, await pg.evaluate('selEdge'), await pg.evaluate('S.edges.length'))
        await b.close()
asyncio.run(main())
