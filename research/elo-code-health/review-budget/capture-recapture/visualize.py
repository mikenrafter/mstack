#!/usr/bin/env python3
"""Self-contained interactive view of the exact finite-pool coverage results."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
TEMPLATE = r'''<!doctype html><html><head><meta charset="utf-8"><style>
body{font-family:var(--font-sans);color:var(--foreground);line-height:1.5}h3{font-size:18px;margin:12px 0 8px}p{margin:8px 0}
.muted,small{color:var(--muted-foreground)}.panel{background:var(--card);border-radius:var(--radius);padding:16px;margin:12px 0}
svg{height:285px;width:100%;display:block}svg text{fill:var(--foreground);font:12px var(--font-sans)}
select{background:var(--secondary);color:var(--foreground);border:1px solid var(--border);border-radius:var(--radius);padding:7px;max-width:100%}
.controls{display:flex;gap:16px;flex-wrap:wrap;align-items:center}input{accent-color:var(--primary)}
table{border-collapse:collapse;width:100%;font-size:13px}td,th{padding:7px;text-align:right;border-bottom:1px solid var(--border)}td:first-child,th:first-child{text-align:left}
.facts{font-family:var(--font-mono);font-size:14px;white-space:pre-line}
</style></head><body>
<h3>Inspection count and known-fault coverage</h3>
<p>Historical human requirements inspections: 8 matrices, 12–14 inspectors each. These curves describe fixed artifacts and study reference faults. They do not predict sequential LLM repair rounds.</p>
<div class="panel"><div class="controls"><label>Artifact/session <select id="matrix"></select></label><label>Inspectors <input id="count" type="range" min="1" max="14" value="2"><span id="count-label">2</span></label></div>
<svg id="coverage" viewBox="0 0 650 285" role="img" aria-label="Exact finite-pool fault coverage by number of inspectors"></svg>
<small>Bold: selected matrix’s mean. Band: 5th–95th percentile of teams in that finite pool, not a confidence interval. Faint: the other matrices. Every team of the selected size has equal weight.</small>
<p id="facts" class="facts"></p></div>
<h3>Additional reference faults found by the next inspector</h3>
<div class="panel"><svg id="marginal" viewBox="0 0 650 285" role="img" aria-label="Mean incremental reference faults by inspection count"></svg>
<small>Each bar is the change in mean coverage from one team size to the next. This is a finite-pool summary; repairs and introduced defects are absent.</small></div>
<table><thead><tr><th>Matrix</th><th>1 inspector</th><th>2</th><th>3</th><th>Full pool</th></tr></thead><tbody id="table"></tbody></table>
<p class="muted">Seven of the eight pools leave some listed faults undetected. The reference list itself is not a census of every possible natural defect. Inspectors and artifacts recur; overlapping teams are not independent experiments.</p>
<p class="muted">Source: <a href="https://www.cs.umd.edu/projects/SoftEng/ESEG/manual/pbr_package/docs/total.cc">UMD PBR laboratory matrices</a>, read as data only. Exact source and parser checks are saved with this research. No round-count or code-approval rule follows from this chart.</p>
<script>const DATA=__DATA__;const matrices=DATA.results;
const select=document.querySelector('#matrix'),slider=document.querySelector('#count');
for(const matrix of matrices){const option=document.createElement('option');option.value=matrix.matrix;option.textContent=matrix.matrix+' — '+matrix.inspectors+' inspectors, '+matrix.reference_defects+' reference faults';select.append(option);}
const NS='http://www.w3.org/2000/svg';function add(svg,tag,attrs,text){const e=document.createElementNS(NS,tag);for(const[k,v]of Object.entries(attrs))e.setAttribute(k,v);if(text!==undefined)e.textContent=text;svg.append(e);return e;}
function axes(svg,maxY,label){svg.replaceChildren();for(let i=0;i<=4;i++){const y=240-i*50;add(svg,'line',{x1:52,x2:620,y1:y,y2:y,stroke:'var(--border)'});add(svg,'text',{x:44,y:y+4,'text-anchor':'end'},(i*maxY/4).toFixed(maxY===100?0:1));}for(let k=0;k<=14;k+=2)add(svg,'text',{x:52+k*40,y:260,'text-anchor':'middle'},k);add(svg,'text',{x:52,y:19},label);add(svg,'text',{x:620,y:280,'text-anchor':'end'},'Inspectors on the same artifact');}
function points(matrix,key,scale){return matrix.curve.map(r=>[52+r.inspectors*40,240-r[key]*scale]);}
function line(svg,pts,color,width,opacity=1){add(svg,'polyline',{points:pts.map(p=>p.join(',')).join(' '),fill:'none',stroke:color,'stroke-width':width,opacity});}
function render(){const chosen=matrices.find(m=>m.matrix===select.value);slider.max=chosen.inspectors;if(+slider.value>chosen.inspectors)slider.value=chosen.inspectors;const k=+slider.value,row=chosen.curve[k-1];document.querySelector('#count-label').textContent=k;
const svg=document.querySelector('#coverage');axes(svg,100,'Study reference faults found (%)');for(const matrix of matrices)if(matrix!==chosen)line(svg,points(matrix,'mean_reference_coverage',200),'var(--muted-foreground)',1,.3);
const band=[...chosen.curve.map(r=>[52+r.inspectors*40,240-200*r.team_p05_found/chosen.reference_defects]),...chosen.curve.toReversed().map(r=>[52+r.inspectors*40,240-200*r.team_p95_found/chosen.reference_defects])];add(svg,'polygon',{points:band.map(p=>p.join(',')).join(' '),fill:'var(--primary)',opacity:.12});line(svg,points(chosen,'mean_reference_coverage',200),'var(--primary)',3);add(svg,'circle',{cx:52+k*40,cy:240-row.mean_reference_coverage*200,r:5,fill:'var(--primary)'});
const next=chosen.curve[k];document.querySelector('#facts').textContent='Mean found: '+row.mean_found.toFixed(2)+' / '+chosen.reference_defects+' ('+(row.mean_reference_coverage*100).toFixed(1)+'%)\nTeam 5th–95th: '+row.team_p05_found+'–'+row.team_p95_found+' reference faults\nNext inspector’s mean addition: '+(next?next.marginal_mean_found.toFixed(2):'not observed beyond this pool')+'\nNever detected anywhere in this pool: '+chosen.never_detected_reference_faults.length+' / '+chosen.reference_defects;
const marginal=document.querySelector('#marginal'),max=Math.max(1,Math.ceil(Math.max(...chosen.curve.map(r=>r.marginal_mean_found))));axes(marginal,max,'Additional reference faults (mean)');for(const r of chosen.curve)add(marginal,'rect',{x:52+r.inspectors*40-10,y:240-200*r.marginal_mean_found/max,width:20,height:200*r.marginal_mean_found/max,fill:r.inspectors===k?'var(--primary)':'var(--chart-2)',opacity:r.inspectors===k?1:.6});}
const table=document.querySelector('#table');for(const matrix of matrices){const tr=document.createElement('tr');for(const text of[matrix.matrix,...[0,1,2,matrix.curve.length-1].map(i=>(100*matrix.curve[i].mean_reference_coverage).toFixed(1)+'%')]){const td=document.createElement('td');td.textContent=text;tr.append(td);}table.append(tr);}select.addEventListener('change',render);slider.addEventListener('input',render);render();
</script></body></html>'''


def main():
    results = json.loads((HERE / 'coverage-results.json').read_text())
    html = TEMPLATE.replace('__DATA__', json.dumps(results, allow_nan=False))
    (HERE / 'coverage.html').write_text(html)
    print(HERE / 'coverage.html')


if __name__ == '__main__':
    main()
