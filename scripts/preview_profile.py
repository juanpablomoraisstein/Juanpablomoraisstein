from pathlib import Path
root=Path(__file__).resolve().parents[1]
(root/'.preview').mkdir(exist_ok=True)
readme=(root/'README.md').read_text()
main=readme[:readme.index('<details>')].replace('"assets/','"../assets/')
audit='''
<script>
(async()=>{
  try{
    const img=document.querySelector('img'); await img.decode();
    const mobile=window.innerWidth<=768;
    if(!img.currentSrc.endsWith(mobile?'terminal-mobile.svg':'terminal-desktop.svg'))throw Error('Wrong responsive source');
    if(document.documentElement.scrollWidth>window.innerWidth)throw Error('Horizontal overflow');
    let source=await (await fetch(img.currentSrc)).text();
    const svg=new DOMParser().parseFromString(source,'image/svg+xml').documentElement;
    svg.style.cssText='position:absolute;left:-10000px;top:0';document.body.append(svg);
    const bounds=svg.getBoundingClientRect();
    const clipped=[];
    for(const node of svg.querySelectorAll('text')){
      if(node.closest('#matrix-rain')) continue;
      const r=node.getBoundingClientRect();
      if(r.width&&(r.left<bounds.left-1||r.right>bounds.right+1||r.top<bounds.top-1||r.bottom>bounds.bottom+1))clipped.push(node.textContent);
    }
    svg.remove();
    if(clipped.length)throw Error('Clipped text: '+JSON.stringify(clipped));
    document.documentElement.dataset.validation='passed';
    const pre=document.createElement('pre');pre.id='validation';pre.hidden=true;
    pre.textContent=JSON.stringify({passed:true,width:innerWidth,mobile,currentSrc:img.currentSrc,clipped:0});document.body.append(pre);
  }catch(error){document.documentElement.dataset.validation='failed';document.body.append(String(error));}
})();
</script>
'''
for theme in ('light','dark'):
 bg,fg,border=('#fff','#1f2328','#d1d9e0') if theme=='light' else ('#0d1117','#e6edf3','#30363d')
 html=f'''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>
*{{box-sizing:border-box}} body{{margin:0;background:{bg};color:{fg};font:16px -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}}main{{max-width:1036px;margin:24px auto;padding:32px;border:1px solid {border};border-radius:6px}}img{{max-width:100%;height:auto;display:block}}p{{line-height:1.8}}a{{color:#4493f8;text-decoration:none}}@media(max-width:768px){{main{{margin:0;padding:16px;border:0}}p{{font-size:12px}}}}
</style></head><body><main>{main}</main>{audit}</body></html>'''
 (root/'.preview'/f'{theme}.html').write_text(html)
