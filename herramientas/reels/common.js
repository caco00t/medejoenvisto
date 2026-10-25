// Motor de animación por tiempo: render(t) determinista para captura cuadro a cuadro.
const cl=x=>x<0?0:x>1?1:x, ease=x=>1-Math.pow(1-cl(x),3),
 eio=x=>{x=cl(x);return x<.5?4*x*x*x:1-Math.pow(-2*x+2,3)/2},
 back=x=>{x=cl(x);const c1=1.70158,c3=c1+1;return 1+c3*Math.pow(x-1,3)+c1*Math.pow(x-1,2)};
const ELS=[...document.querySelectorAll('[data-in]')];
ELS.forEach(e=>{ if(e.dataset.fx==='type'){ e.dataset.full=e.textContent; } });
function vis(t,a,b,d){ if(t<a||t>b)return 0; return Math.min(ease((t-a)/d),ease((b-t)/d)); }
function render(t){
 for(const e of ELS){
  const a=+e.dataset.in,b=+(e.dataset.out||999),fx=e.dataset.fx||'fade';
  const d=+(e.dataset.d|| (fx==='cut'?0.06:0.3));
  let v=vis(t,a,b,d), tr='';
  const p=(t-a)/d;
  switch(fx){
   case 'up': tr=`translateY(${(1-v)*60}px)`; break;
   case 'down': tr=`translateY(${(1-v)*-60}px)`; break;
   case 'pop': tr=`scale(${t<a+d? 0.6+0.4*back(p):0.6+0.4*v})`; break;
   case 'stamp': { const s=t<a+0.25? 2.4-1.4*ease((t-a)/0.25):1; tr=`rotate(-8deg) scale(${s})`; if(t>=a&&t<a+0.25)v=ease((t-a)/0.25); break; }
   case 'left': tr=`translateX(${(1-v)*-120}px)`; break;
   case 'right': tr=`translateX(${(1-v)*120}px)`; break;
   case 'bubble-in': tr=`translateX(${(1-v)*-40}px) scale(${0.85+0.15*back(p)})`; break;
   case 'bubble-out': tr=`translateX(${(1-v)*40}px) scale(${0.85+0.15*back(p)})`; break;
   case 'type': { const full=e.dataset.full, dur=+(e.dataset.td||1); const n=Math.round(full.length*cl((t-a)/dur));
     e.textContent=full.slice(0,n); v=(t>=a&&t<=b)?1:0; break; }
   case 'cut': break;
  }
  if(e.dataset.base) tr=e.dataset.base+' '+tr;
  e.style.opacity=v; e.style.transform=tr;
 }
 if(window.extra) window.extra(t);
}
window.render=render;
