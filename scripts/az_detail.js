// Maricopa AQ Data Viewer: save the text of each Emissions Inventory detail page. Skips ones already saved.
const { chromium } = require('playwright');
const fs = require('fs');
const DIR = '/srv/airtox/nei/raw_state/az/ei';
const jobs = JSON.parse(fs.readFileSync('/srv/airtox/nei/raw_state/az/jobs.json'));
(async () => {
  const b = await chromium.launch();
  let p = null, done = 0;
  const fresh = async () => {
    if (p) await p.close();
    p = await b.newPage({viewport: {width: 1400, height: 1000}, userAgent: 'dcair-research/0.1 (zer0contextlost@proton.me) Playwright'});
    await p.goto('https://aqdata.maricopa.gov/disclaimer.jsf', {waitUntil: 'networkidle'});
    await p.locator('img[alt="Agree"]').first().click(); await p.waitForTimeout(3000);
  };
  await fresh();
  for (const j of jobs) {
    const out = `${DIR}/${j.ei}.txt`;
    if (fs.existsSync(out)) continue;
    for (let attempt = 0; attempt < 3; attempt++) {
      try {
        await p.getByText('Emissions Inventories', {exact: true}).first().click(); await p.waitForTimeout(3000);
        await p.fill('[id="_idJsp7:eiSearch_FacilityName"]', j.name);
        await p.locator('img[alt="Submit"]').first().click(); await p.waitForTimeout(5000);
        const sel = p.locator('select:has(option[value="all"])');
        if (await sel.count()) { await sel.first().selectOption('all'); await p.waitForTimeout(5000); }
        await p.getByText(j.ei, {exact: true}).first().click(); await p.waitForTimeout(6000);
        const t = (await p.innerText('body')).replace(/\n\s*\n/g, '\n');
        if (!t.includes(j.ei)) throw new Error('detail page missing id');
        fs.writeFileSync(out, t); done++;
        console.log(`ok ${j.ei} ${j.fid} ${j.year} (${done})`);
        break;
      } catch (e) {
        console.log(`retry ${j.ei} attempt ${attempt}: ${e.message.split('\n')[0]}`);
        await fresh();
      }
    }
    await p.waitForTimeout(2000);
  }
  console.log('finished', done);
  await b.close();
})();
