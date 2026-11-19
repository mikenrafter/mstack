#!/usr/bin/env python3
"""Generate the explanatory chart; inputs are preserved experiment outputs.

The Beta curves illustrate an independent-Bernoulli assumption, not a fitted
posterior for the historical review corpus. See uncertainty/README.md.
"""
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main():
    grid = json.loads((HERE / 'models/accepted-grid-results.json').read_text())
    fitted = json.loads((HERE / 'models/accepted-results.json').read_text())
    baseline = fitted['loco']['metrics']['pooled']['brier']
    if grid['input_sha256'] != fitted['input_sha256']:
        raise ValueError('The grid and baseline use different observations')
    empirical = {key: 100 * (metrics['brier'] / baseline - 1)
                 for key, metrics in grid['metrics'].items()}
    curves = []
    for shape in (1, 10, 100):
        log_normalizer = math.lgamma(2 * shape) - 2 * math.lgamma(shape)
        density = []
        for step in range(201):
            probability = step / 200
            if shape == 1:
                value = 1.0
            elif probability in (0, 1):
                value = 0.0
            else:
                value = math.exp(log_normalizer + (shape - 1) * (
                    math.log(probability) + math.log1p(-probability)))
            density.append(value)
        curves.append({'shape': shape, 'density': density})
    payload = json.dumps({'empirical': empirical, 'curves': curves,
                          'baseline': baseline}, allow_nan=False)
    html = TEMPLATE.replace('__PAYLOAD__', payload)
    destination = HERE / 'uncertainty.html'
    destination.write_text(html)
    print(destination)


TEMPLATE = r'''<!doctype html><html><head><meta charset="utf-8"><style>
body{font-family:var(--font-sans);color:var(--foreground);line-height:1.5}
h3{font-size:18px;margin:16px 0 8px}p{margin:8px 0;color:var(--muted-foreground)}
svg{width:100%;height:260px;display:block;overflow:visible}text{fill:var(--foreground);font:12px var(--font-sans)}
.panel{background:var(--card);border-radius:var(--radius);padding:16px;margin:12px 0}
.controls{display:flex;gap:16px;flex-wrap:wrap;align-items:center}input{accent-color:var(--primary);max-width:160px}
.numbers{font-family:var(--font-mono);font-size:14px;white-space:pre-line}
small{color:var(--muted-foreground)}button{background:var(--secondary);color:var(--foreground);border:1px solid var(--border);border-radius:var(--radius);padding:6px 10px;cursor:pointer}
</style></head><body>
<h3>The K sweep did not improve the forecast</h3>
<p>Higher is worse: increase in Brier loss relative to the training-only prevalence forecast. Every point uses the same 39 historical rounds, with each change held out of fitting.</p>
<div class="panel"><svg id="sweep" viewBox="0 0 650 260" role="img" aria-label="All eight Elo K variants have higher loss than prevalence"></svg>
<small>Fixed K: solid line. Evidence-decayed K: dashed line, K = K₀/(1 + preceding change groups/4). These are exploratory comparisons across six projects; group independence is unestablished.</small></div>
<h3>K is an update size; uncertainty needs its own model</h3>
<p>These synthetic Beta distributions all predict a 50% chance of a finding. Their widths differ because their assumed prior evidence differs. They are illustrations, not calibrated posteriors for your code.</p>
<div class="panel"><svg id="density" viewBox="0 0 650 260" role="img" aria-label="Beta probability densities with equal mean and different concentration"></svg>
<div class="controls"><button data-shape="1">Beta(1,1)</button><button data-shape="10">Beta(10,10)</button><button data-shape="100">Beta(100,100)</button></div></div>
<div class="panel"><div class="controls"><label>Assumed probability <input id="probability" type="range" min="5" max="95" value="50"></label>
<label>Prior strength a+b <input id="strength" type="range" min="2" max="200" value="20"></label></div>
<p class="numbers" id="readout"></p>
<small>R = 1500 + 400 log₁₀(a/b). After a finding, a increases by 1; after a complete review with no finding, b increases by 1. The equivalent K generally differs by outcome. Unknown or unperformed reviews contribute neither outcome. Repeated reviews on one change are correlated and do not supply this model’s independent evidence.</small></div>
<p>Practical implication: record which snapshot and contracts each review covered, what its fixes changed, and whether a later finding was verified. Changing K cannot recover missing observations or distinguish reviewer sensitivity from code risk.</p>
<script>const DATA=__PAYLOAD__;
const NS='http://www.w3.org/2000/svg';
function add(svg,tag,attributes,text){const e=document.createElementNS(NS,tag);for(const [key,value] of Object.entries(attributes))e.setAttribute(key,value);if(text!==undefined)e.textContent=text;svg.append(e);return e;}
function axes(svg,maxY,label){for(let i=0;i<=3;i++){const y=220-i*60;add(svg,'line',{x1:58,x2:620,y1:y,y2:y,stroke:'var(--border)'});add(svg,'text',{x:48,y:y+4,'text-anchor':'end'},(i*maxY/3).toFixed(maxY===3?0:1));}add(svg,'text',{x:58,y:16},label);}
const sweep=document.querySelector('#sweep');axes(sweep,3,'Higher forecast loss (%)');
for(const [index,k] of [8,16,32,64].entries()){add(sweep,'text',{x:75+index*175,y:246,'text-anchor':'middle'},'K₀ '+k);}
for(const [schedule,color] of [['fixed','var(--chart-1)'],['decay','var(--chart-2)']]){const points=[8,16,32,64].map((k,i)=>[75+i*175,220-DATA.empirical['K'+k+'_'+schedule]*60]);add(sweep,'polyline',{points:points.map(p=>p.join(',')).join(' '),fill:'none',stroke:color,'stroke-width':2,'stroke-dasharray':schedule==='decay'?'6 4':'none'});for(const [i,p] of points.entries()){add(sweep,'circle',{cx:p[0],cy:p[1],r:4,fill:color});add(sweep,'text',{x:p[0],y:p[1]-10,'text-anchor':'middle'},'+'+DATA.empirical['K'+[8,16,32,64][i]+'_'+schedule].toFixed(2)+'%');}}
let selected=10;
function density(){const svg=document.querySelector('#density');svg.replaceChildren();axes(svg,12,'Probability density');for(let i=0;i<=4;i++)add(svg,'text',{x:58+i*140,y:246,'text-anchor':'middle'},(i/4).toFixed(2));for(const [index,curve] of DATA.curves.entries()){const points=curve.density.map((v,i)=>(58+560*i/200)+','+(220-180*v/12)).join(' ');add(svg,'polyline',{points,fill:'none',stroke:'var(--chart-'+(index+1)+')','stroke-width':curve.shape===selected?3:1.5,opacity:curve.shape===selected?1:.35});}add(svg,'text',{x:330,y:32,'text-anchor':'middle'},'Selected: Beta('+selected+','+selected+')');}
function readout(){const p=+document.querySelector('#probability').value/100,n=+document.querySelector('#strength').value,a=p*n,b=(1-p)*n;const up=400*Math.log10(1+1/a),down=400*Math.log10(1+1/b);document.querySelector('#readout').textContent='p = '+p.toFixed(2)+'; a = '+a.toFixed(2)+'; b = '+b.toFixed(2)+'\nFinding: rating +'+up.toFixed(2)+'; equivalent K = '+(up/(1-p)).toFixed(2)+'\nNo finding: rating −'+down.toFixed(2)+'; equivalent K = '+(down/p).toFixed(2);}
document.querySelectorAll('button[data-shape]').forEach(button=>button.addEventListener('click',()=>{selected=+button.dataset.shape;document.querySelector('#probability').value=50;document.querySelector('#strength').value=2*selected;density();readout();}));document.querySelectorAll('input').forEach(input=>input.addEventListener('input',readout));density();readout();
</script></body></html>'''


if __name__ == '__main__':
    main()
