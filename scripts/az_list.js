const { chromium } = require('playwright');
const names = process.argv.slice(2);
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({viewport:{width:1400,height:1000}});
  await p.goto('https://aqdata.maricopa.gov/disclaimer.jsf', {waitUntil:'networkidle'});
  await p.locator('img[alt="Agree"]').first().click(); await p.waitForTimeout(3000);
  for (const n of names) {
    await p.getByText('Emissions Inventories', {exact:true}).first().click(); await p.waitForTimeout(3000);
    await p.fill('[id="_idJsp7:eiSearch_FacilityName"]', n);
    await p.locator('img[alt="Submit"]').first().click(); await p.waitForTimeout(5000);
    const sel = p.locator('select:has(option[value="all"])'); if (await sel.count()) { await sel.first().selectOption('all'); await p.waitForTimeout(6000); }
    const t = await p.innerText('body');
    console.log('### ', n); t.split('\n').filter(l=>/^EI\d/.test(l)).forEach(l=>console.log(l));
  }
  await b.close();
})();
