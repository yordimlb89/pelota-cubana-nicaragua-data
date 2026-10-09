"""Compile exact reviewed identities; replace cumulative blocks, never add snapshots."""
import copy,json,re,unicodedata
from decimal import Decimal,ROUND_HALF_UP
from pathlib import Path
ROOT=Path(__file__).parent
KINDS=('batting','pitching','fielding')
def norm(s):return ' '.join(''.join(c for c in unicodedata.normalize('NFD',s) if not unicodedata.combining(c)).lower().split())
def rate(n,d,places=3):
 if not d:return None
 s=str((Decimal(n)/Decimal(d)).quantize(Decimal(10)**-places,rounding=ROUND_HALF_UP))
 return s[1:] if places==3 and s.startswith('0.') else s
def compile_data(source):
 players=source['players'];aliases={}
 for p in players:
  for a in [p['name'],*p['aliases']]:
   key=norm(a);assert key not in aliases or aliases[key]==p['id'],('Ambiguous alias',a);aliases[key]=p['id']
 rows={};reviews=[]
 for t in source['tables']:
  for values in t['rows']:
   assert len(values)==len(t['headers']),('Width mismatch',t['season'])
   d=dict(zip(t['headers'],values));name=d.pop('Player');team=d.pop('Team');pid=aliases.get(norm(name))
   if not pid:continue
   phase=t.get('phase','all-rounds');key=(t['season'],phase,pid,team)
   r=rows.setdefault(key,{'playerId':pid,'year':int(t['season'][:4]),'season':t['season'],'phase':phase,'team':team,'sourceName':name.replace('\n',' '),'sources':[]})
   assert t['kind'] not in r,('Duplicate',key,t['kind'])
   r[t['kind']]={k:(None if v in ('','---','-','—') else v) for k,v in d.items()}
   if t['url'] not in r['sources']:r['sources'].append(t['url'])
 for r in rows.values():
  def apply(d,kind,k,v):
   old=d.get(k)
   if old!=v:reviews.append({'playerId':r['playerId'],'season':r['season'],'phase':r['phase'],'team':r['team'],'kind':kind,'stat':k,'published':old,'calculated':v})
   d[k]=v
  b=r.get('batting');p=r.get('pitching');f=r.get('fielding')
  if b:
   n={k:int(b[k]) for k in ('AB','H','2B','3B','HR','BB','HBP','SF','TB')}
   assert n['H']<=n['AB'] and n['2B']+n['3B']+n['HR']<=n['H'],r
   assert n['TB']==n['H']+n['2B']+2*n['3B']+3*n['HR'],r
   den=n['AB']+n['BB']+n['HBP']+n['SF'];on=n['H']+n['BB']+n['HBP']
   apply(b,'batting','AVG',rate(n['H'],n['AB']));apply(b,'batting','SLG',rate(n['TB'],n['AB']));apply(b,'batting','OBP',rate(on,den));apply(b,'batting','OPS',rate(on*n['AB']+n['TB']*den,den*n['AB']))
  if p:
   whole,part=(p['IP'].split('.')+['0'])[:2];assert int(part) in (0,1,2);outs=int(whole)*3+int(part);r['pitchingOuts']=outs
   assert int(p['ER'])<=int(p['R']),r
   apply(p,'pitching','ERA',rate(int(p['ER'])*27,outs,2));apply(p,'pitching','WHIP',rate((int(p['H'])+int(p['BB']))*3,outs,2));apply(p,'pitching','BAVG',rate(int(p['H']),int(p['AB'])))
  if f:
   assert int(f['C'])==int(f['PO'])+int(f['A'])+int(f['E']),r
   apply(f,'fielding','FLDP',rate(int(f['PO'])+int(f['A']),int(f['C'])))
 records=[r for r in rows.values() if any(int((r.get(k)or{}).get(metric)or 0)>0 for k,metric in [('batting','G'),('pitching','APP'),('fielding','G'),('fielding','C')])]
 used={r['playerId'] for r in records}
 return {k:copy.deepcopy(source[k]) for k in ('schema','league','reviewedAt','coverage','seasons','teams')}|{'players':[p for p in players if p['id'] in used],'records':records,'ratioReviews':reviews,'updateStatus':source.get('updateStatus',{'mode':'reviewed-import','manualReviewDate':'2026-10-09','message':'Importación histórica revisada. Actualización automática pendiente de primera comprobación.'})}
if __name__=='__main__':
 source=json.loads((ROOT/'source.json').read_text());data=compile_data(source);(ROOT/'data.json').write_text(json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n');print(json.dumps({'players':len(data['players']),'records':len(data['records']),'ratioReviews':len(data['ratioReviews']),'seasons':{s['season']:len([r for r in data['records'] if r['season']==s['season']]) for s in data['seasons']}}))
