"""Independent APBN updater. Official cumulative tables; no Serie Nacional access."""
import copy,json,re,sys
from datetime import datetime,timezone
from pathlib import Path
from playwright.sync_api import sync_playwright
from compile import compile_data,norm,KINDS
ROOT=Path(__file__).parent
STAMP=datetime.now(timezone.utc).isoformat().replace('+00:00','Z')
def snapshot(page):
 return page.locator('#table-stats').evaluate('''table=>({headers:[...table.querySelectorAll('thead th')].map(x=>x.innerText.trim()),rows:[...table.querySelectorAll('tbody tr')].map(r=>[...r.querySelectorAll('td')].map(c=>c.innerText.trim())),info:document.querySelector('#table-stats_info')?.textContent,next:document.querySelector('#table-stats_next')?.className})''')
def capture(page,season,kind,heading,marker):
 page.get_by_role('heading',name=heading,exact=True).click()
 page.locator('#table-stats thead th').get_by_text(marker,exact=True).wait_for(timeout=45000)
 page.locator('#table-stats tbody tr').first.wait_for(timeout=45000)
 rows=[];pages=set();headers=None;total=None
 while True:
  s=snapshot(page);match=re.search(r'of\s+([\d,]+)\s+entries',s['info']or'')
  if not match:raise ValueError('Missing total count: '+str(s['info']))
  total=int(match[1].replace(',',''))
  if total==0:raise ValueError('Empty official table: '+season['season']+' '+kind)
  if s['info'] in pages:raise ValueError('Repeated pagination page')
  pages.add(s['info']);headers=headers or s['headers']
  if headers!=s['headers'] or any(len(r)!=len(headers) for r in s['rows']):raise ValueError('Schema drift')
  rows.extend(s['rows'])
  if 'disabled' in (s['next']or''):break
  before=s['info'];page.locator('#table-stats_next').click()
  page.wait_for_function('(old)=>document.querySelector("#table-stats_info")?.textContent!==old',arg=before,timeout=20000)
 if len(rows)!=total or len({(norm(r[0]),r[1]) for r in rows})!=total:raise ValueError('Missing/duplicate source rows')
 return {'season':season['season'],'kind':kind,'url':season['url'],'headers':headers,'rows':rows,'reviewedRows':total,'checkedAt':STAMP}
def run():
 source=json.loads((ROOT/'source.json').read_text());source['players']=json.loads((ROOT/'registry.json').read_text())
 original=copy.deepcopy(source);errors=[];verified=[];waiting=[]
 with sync_playwright() as p:
  browser=p.chromium.launch();page=browser.new_page()
  for season in source['seasons'][-2:]:
   if season.get('startDate','')>STAMP[:10]:waiting.append(season['season']);continue
   try:
    response=page.goto(season['url'],wait_until='domcontentloaded',timeout=60000)
    if not response or response.status>=400:raise ValueError('Official site HTTP '+str(response.status if response else None)+'; '+page.locator('body').inner_text()[:250])
    fresh=[capture(page,season,*args) for args in [('batting','Batting','OPS'),('pitching','Pitching','WHIP'),('fielding','Fielding','FLDP')]]
    old=[t for t in source['tables'] if t['season']==season['season']]
    for table in fresh:
     prior=next((t for t in old if t['kind']==table['kind']),None)
     if prior and len(table['rows'])<len(prior['rows'])*.8:raise ValueError('Unexpected loss of source rows')
    trial=copy.deepcopy(source);trial['tables']=[t for t in source['tables'] if t['season']!=season['season']]+fresh
    compile_data(trial) # All mathematical/identity checks before replacing an edition.
    source=trial;verified.append(season['season'])
    target=next(s for s in source['seasons'] if s['season']==season['season']);target['checkedAt']=STAMP;target['status']='available'
   except Exception as e:errors.append({'season':season['season'],'message':str(e)[:400]})
  browser.close()
 source['updateStatus']={'mode':'github-actions','lastAttemptAt':STAMP,'lastSuccessAt':STAMP if verified else original.get('updateStatus',{}).get('lastSuccessAt','2026-10-09T19:00:00Z'),'verifiedSeasons':verified,'waitingSeasons':waiting,'errors':errors,'partial':bool(errors),'message':'Actualización parcial; se conservan las últimas tablas verificadas.' if errors else 'Consulta oficial completada. Las temporadas aún no iniciadas esperan su fecha de comienzo.'}
 data=compile_data(source)
 for path,obj in [('source.json',source),('data.json',data),('status.json',source['updateStatus'])]:
  (ROOT/path).write_text(json.dumps(obj,ensure_ascii=False,separators=(',',':'))+'\n')
 print(json.dumps(source['updateStatus'],ensure_ascii=False))
 return 1 if errors else 0
if __name__=='__main__':sys.exit(run())
