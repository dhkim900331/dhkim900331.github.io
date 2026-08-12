const CATEGORIES = ['Ansible','APM','Coherence','DataBase','ETC','Java','JBoss','JDBC','Jekyll','Jenkins','Mermaid','MSW','Network','ODI','OS','Programming','Putty','RHCSA','Scripts','SSL','Typora','WebLogic','WebTier'];
const source = document.querySelector('#source');
const rendered = document.querySelector('#rendered');
const category = document.querySelector('#category');
const slug = document.querySelector('#slug');
const status = document.querySelector('#status');
const fileName = document.querySelector('#fileName');
let rootHandle, postHandle, normalizing = false;

CATEGORIES.forEach(name => category.add(new Option(name, name)));
category.value = 'WebLogic';
const esc = value => value.replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const inline = value => esc(value)
  .replace(/!\[([^\]]*)\]\((\/assets\/[^)\s]+)(?:\s+"[^"]*")?\)/g, '<img alt="$1" src="$2">')
  .replace(/\[([^\]]+)\]\((https?:\/\/[^)\s]+|\/[^)\s]+)\)/g, '<a href="$2" target="_blank" rel="noreferrer">$1</a>')
  .replace(/`([^`]+)`/g, '<code>$1</code>').replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');

function render(markdown) {
  const chunks = markdown.split(/(^```[\s\S]*?^```$)/m);
  rendered.innerHTML = chunks.map(chunk => {
    if (chunk.startsWith('```')) return `<pre><code>${esc(chunk.replace(/^```[^\n]*\n?|\n?```$/g,''))}</code></pre>`;
    const lines = chunk.split('\n'); let html='', inList=false;
    for (const line of lines) {
      const heading=line.match(/^(#{1,6})\s+(.+)$/); const item=line.match(/^[-*]\s+(.+)$/);
      if (heading) { if(inList){html+='</ul>';inList=false;} html+=`<h${heading[1].length}>${inline(heading[2])}</h${heading[1].length}>`; }
      else if(item) { if(!inList){html+='<ul>';inList=true;} html+=`<li>${inline(item[1])}</li>`; }
      else { if(inList){html+='</ul>';inList=false;} if(line.trim()==='') html+=''; else if(line.trim()==='<br>'||line.trim()==='<br><br>') html+=line; else if(line.startsWith('> ')) html+=`<blockquote>${inline(line.slice(2))}</blockquote>`; else html+=`<p>${inline(line)}</p>`; }
    }
    return html+(inList?'</ul>':'');
  }).join('');
}

function outsideFences(text, transform) {
  return text.split(/(^```[\s\S]*?^```$)/m).map(part => part.startsWith('```') ? part : transform(part)).join('');
}
function normalizeBreaks() {
  if (normalizing) return;
  const one = Math.max(2, Number(document.querySelector('#oneBreak').value) || 2);
  const two = Math.max(one + 1, Number(document.querySelector('#twoBreak').value) || 4);
  const before = source.value;
  const after = outsideFences(before, text => text.replace(/\n{2,}/g, run => `${run.length >= two ? '<br><br>' : '<br>'}\n`));
  if (before !== after) { normalizing=true; const pos=source.selectionStart + (after.length-before.length); source.value=after; source.selectionStart=source.selectionEnd=Math.max(0,pos); normalizing=false; }
}
function updatePreview() { render(source.value); }
source.addEventListener('input', () => { normalizeBreaks(); updatePreview(); });
source.addEventListener('keydown', event => { if(event.key==='Tab'){event.preventDefault(); const p=source.selectionStart; source.setRangeText('  ',p,source.selectionEnd,'end'); source.dispatchEvent(new Event('input'));} });

async function verifyPermission(handle, write=true) { const mode=write?{mode:'readwrite'}:{mode:'read'}; if ((await handle.queryPermission(mode))==='granted') return true; return (await handle.requestPermission(mode))==='granted'; }
async function directory(handle, name) { return handle.getDirectoryHandle(name, {create:true}); }
async function postDirectory() { if(!rootHandle) throw new Error('먼저 블로그 저장소를 선택하세요.'); const c=await rootHandle.getDirectoryHandle(category.value); return directory(c, '_posts'); }
function currentSlug() { const value=slug.value.trim(); if(!/^[A-Za-z0-9][A-Za-z0-9._-]*$/.test(value)) throw new Error('slug는 영문, 숫자, 점, 밑줄, 하이픈만 사용할 수 있습니다.'); return value; }
async function nextPrefix(dir) { let max=0; for await(const [name] of dir.entries()){const m=name.match(/^0000-(\d{2})-(\d{2})-.*\.md$/); if(m) max=Math.max(max,Number(m[1])*100+Number(m[2]));} const next=max+1; return `0000-${String(Math.floor(next/100)).padStart(2,'0')}-${String(next%100).padStart(2,'0')}`; }
function nowKst() { const kst=new Date(Date.now()+9*3600*1000); return kst.toISOString().replace('T',' ').slice(0,19)+' +0900'; }

document.querySelector('#chooseRoot').onclick=async()=>{ try { rootHandle=await window.showDirectoryPicker({mode:'readwrite'}); if(!(await verifyPermission(rootHandle))) throw new Error('폴더 쓰기 권한이 필요합니다.'); status.textContent=`저장소 선택됨: ${rootHandle.name}`; } catch(e) { status.textContent=e.message; } };
document.querySelector('#newPost').onclick=async()=>{ try { const dir=await postDirectory(); const name=`${await nextPrefix(dir)}-${currentSlug()}.md`; postHandle=await dir.getFileHandle(name,{create:true}); source.value=`---\nlayout: post\ntitle: "[${category.value}] "\ndate: ${nowKst()}\ntags: [${category.value}]\ntypora-root-url: ../..\n---\n\n# 1. Overview\n\n# 2. Descriptions\n\n# 3. References\n`; fileName.textContent=`${category.value}/_posts/${name}`; status.textContent='새 글이 준비되었습니다. 저장을 누르면 기록됩니다.'; updatePreview(); } catch(e) { status.textContent=e.message; } };
document.querySelector('#openPost').onclick=async()=>{ try { [postHandle]=await window.showOpenFilePicker({types:[{description:'Markdown',accept:{'text/markdown':['.md']}}]}); source.value=await (await postHandle.getFile()).text(); const m=postHandle.name.match(/^0000-\d\d-\d\d-(.+)\.md$/); if(m) slug.value=m[1]; fileName.textContent=postHandle.name; status.textContent='기존 글을 열었습니다.'; updatePreview(); } catch(e) { status.textContent=e.message; } };
document.querySelector('#save').onclick=async()=>{ try { if(!postHandle) throw new Error('새 글을 만들거나 기존 글을 먼저 여세요.'); const w=await postHandle.createWritable(); await w.write(source.value); await w.close(); status.textContent='저장했습니다.'; } catch(e) { status.textContent=e.message; } };
async function importImage(file) { try { if(!rootHandle) throw new Error('먼저 블로그 저장소를 선택하세요.'); const postSlug=currentSlug(); let target=await directory(rootHandle,'assets'); target=await directory(target,'posts'); target=await directory(target,'images'); target=await directory(target,category.value); target=await directory(target,postSlug); const safe=file.name.replace(/[^A-Za-z0-9._-]/g,'-'); const output=await target.getFileHandle(`${Date.now()}-${safe}`, {create:true}); const writable=await output.createWritable(); await writable.write(file); await writable.close(); const url=`/assets/posts/images/${category.value}/${postSlug}/${output.name}`; const at=source.selectionStart; source.setRangeText(`![${document.querySelector('#imageAlt').value.trim() || safe}](${url})`,at,source.selectionEnd,'end'); source.dispatchEvent(new Event('input')); status.textContent=`이미지를 복사하고 URL을 삽입했습니다: ${url}`; } catch(e) { status.textContent=e.message; } }
document.querySelector('#importImage').onclick=()=>document.querySelector('#imagePicker').click();
document.querySelector('#imagePicker').onchange=e=>{if(e.target.files[0]) importImage(e.target.files[0]); e.target.value='';};
source.addEventListener('dragover',e=>e.preventDefault()); source.addEventListener('drop',e=>{e.preventDefault(); const image=[...e.dataTransfer.files].find(f=>f.type.startsWith('image/')); if(image) importImage(image);});
updatePreview();
