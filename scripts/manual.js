(() => {
  'use strict';
  const $ = s => document.querySelector(s);
  const data = JSON.parse($('#search-data').textContent);
  const fold = s => s.toLocaleLowerCase('de').normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/ß/g, 'ss');
  const indexed = data.map(d => ({...d, hay:fold(d.title+' '+d.text+' '+d.keywords), titleFold:fold(d.title)}));
  const reading=$('#reading'), results=$('#results'), input=$('#search');
  let timer, lastQuery='', terms=[];
  const escape = s => s.replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  function marked(s) {
    if(!terms.length) return escape(s);
    const rawTerms=input.value.trim().split(/\s+/).filter(Boolean).map(t=>t.replace(/[.*+?^${}()|[\]\\]/g,'\\$&'));
    const re=new RegExp('('+rawTerms.join('|')+')','gi');
    return s.split(re).map((part,i)=>i%2?'<mark>'+escape(part)+'</mark>':escape(part)).join('');
  }
  function search() {
    lastQuery=input.value.trim(); terms=fold(lastQuery).split(/\s+/).filter(Boolean);
    if(!terms.length){results.hidden=true;reading.hidden=false;return;}
    const hits=indexed.filter(d=>terms.every(t=>d.hay.includes(t))).sort((a,b)=> {
      const score=d=>terms.reduce((n,t)=>n+(d.titleFold.includes(t)?10:0),0);
      return score(b)-score(a)||a.id-b.id;
    });
    results.hidden=false;reading.hidden=true;
    window.scrollTo({top:0,behavior:'instant'});
    $('#result-count').textContent=hits.length+' '+(hits.length===1?'Thema gefunden':'Themen gefunden');
    $('#result-list').innerHTML=hits.map(d=>{
      const at=Math.max(0,fold(d.text).indexOf(terms[0])-90);
      const snippet=(at?'… ':'')+d.text.slice(at,at+290).replace(/\s+/g,' ')+(d.text.length>at+290?' …':'');
      return '<li><small>'+escape(d.chapter)+'</small><a href="#topic-'+d.id+'">'+escape(d.number)+' '+marked(d.title)+'</a><p>'+marked(snippet)+'</p></li>';
    }).join('') || '<li>Keine Treffer. Versuchen Sie einen kürzeren Begriff oder eine andere Schreibweise.</li>';
  }
  function clearSearch(){input.value='';lastQuery='';terms=[];search();}
  input.addEventListener('input',()=>{clearTimeout(timer);timer=setTimeout(search,120);});
  $('#clear').addEventListener('click',()=>{clearSearch();input.focus();});
  document.addEventListener('keydown',e=>{if((e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==='k'){e.preventDefault();document.body.classList.add('nav-open');$('#menu').setAttribute('aria-expanded','true');input.focus();input.select();}});
  $('#menu').addEventListener('click',()=>{const open=document.body.classList.toggle('nav-open');$('#menu').setAttribute('aria-expanded',String(open));});
  function tabs(index){$('#outline').hidden=index;$('#index-panel').hidden=!index;$('#contents-tab').classList.toggle('active',!index);$('#index-tab').classList.toggle('active',index);}
  $('#contents-tab').addEventListener('click',()=>tabs(false));$('#index-tab').addEventListener('click',()=>tabs(true));
  function activate(id) {
    document.querySelectorAll('#outline a.active').forEach(a=>a.classList.remove('active'));
    const a=document.querySelector('#outline a[data-topic="'+id+'"]');
    if(a){a.classList.add('active');const d=a.closest('details');if(d)d.open=true;}
    const n=Number(id),prev=$('#prev-topic'),next=$('#next-topic');
    prev.href=n>0?'#topic-'+(n-1):'#start';next.href=n<243?'#topic-'+(n+1):'#edition';
    prev.textContent=n>0?'← '+data[n-1].title:'← Übersicht';next.textContent=n<243?data[n+1].title+' →':'Über diese Ausgabe →';
    $('#position').textContent=(n+1)+' / 244';
  }
  function navigate(hash, update=true){
    const el=document.getElementById(hash.slice(1)); if(!el)return;
    results.hidden=true;reading.hidden=false;
    if(update&&location.hash!==hash)history.pushState(null,'',hash);
    document.body.classList.remove('nav-open');$('#menu').setAttribute('aria-expanded','false');
    if(hash.startsWith('#topic-'))activate(hash.slice(7));
    requestAnimationFrame(()=>el.scrollIntoView({behavior:'instant',block:'start'}));
  }
  document.addEventListener('click',e=>{
    const a=e.target.closest('a[href^="#"]');if(a){e.preventDefault();navigate(a.getAttribute('href'));}
    const img=e.target.closest('.topic img');
    if(img){$('#large-image').src=img.src;$('#large-image').alt=img.alt;$('#image-caption').textContent=img.closest('section').querySelector('h2').textContent.trim();$('#lightbox').showModal();}
  });
  $('#close-image').addEventListener('click',()=>$('#lightbox').close());
  $('#lightbox').addEventListener('click',e=>{if(e.target===$('#lightbox'))$('#lightbox').close();});
  $('#top').addEventListener('click',()=>navigate('#start'));
  window.addEventListener('popstate',()=>navigate(location.hash||'#start',false));
  const observer=new IntersectionObserver(entries=>{for(const e of entries)if(e.isIntersecting)activate(e.target.dataset.topic);},{rootMargin:'-90px 0px -65% 0px'});
  document.querySelectorAll('.topic').forEach(s=>observer.observe(s));
  if(location.hash)navigate(location.hash,false);
})();
