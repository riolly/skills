/* Evaluate this file once with T3 preview_evaluate, then call __walkthrough.mark(). */
(() => {
  window.__walkthrough?.destroy();
  const attr = (element, values) => Object.entries(values).forEach(([k,v]) => element.setAttribute(k, v));
  const add = (parent, name, values = {}) => {
    const element = parent.appendChild(document.createElementNS('http://www.w3.org/2000/svg', name));
    attr(element, values);
    return element;
  };
  // Build nodes and set styles through CSSOM. A page with Trusted Types or a strict
  // style-src policy rejects innerHTML and inline <style>.
  const host = document.createElement('div');
  host.setAttribute('data-walkthrough-overlay', '');
  host.setAttribute('aria-hidden', 'true');
  host.style.cssText = 'all:initial;position:fixed;inset:0;z-index:2147483647;pointer-events:none;';
  const root = host.attachShadow({ mode: 'open' });
  const svg = add(root, 'svg');
  Object.assign(svg.style, { position:'absolute', inset:'0', width:'100%', height:'100%', overflow:'visible' });
  const marks = add(svg, 'g', { fill:'none', stroke:'#f97316', 'stroke-width':4 });
  const circle = add(marks, 'ellipse');
  const rectangle = add(marks, 'rect', { rx:8 });
  const pointer = add(svg, 'g');
  add(pointer, 'circle', { r:15, fill:'#f9731640', stroke:'#f97316', 'stroke-width':2 });
  add(pointer, 'path', { d:'M0 0 L0 24 L6 18 L11 29 L16 27 L11 16 L20 16 Z',
    fill:'#fff', stroke:'#142033', 'stroke-width':2, 'stroke-linejoin':'round' });
  const label = root.appendChild(document.createElement('div'));
  Object.assign(label.style, { position:'absolute', maxWidth:'min(420px,80vw)', padding:'8px 12px',
    borderRadius:'8px', background:'#142033', color:'white', font:'600 17px/1.35 sans-serif',
    boxShadow:'0 2px 10px #0005', boxSizing:'border-box' });
  for (const element of [svg, label]) element.style.setProperty('pointer-events', 'none', 'important');
  document.documentElement.append(host);
  // z-index cannot reach above a modal dialog, popover, or fullscreen element. Those are in the
  // browser's top layer, which stacks by entry order, so the overlay joins it again for every mark.
  const raise = () => {
    if (!host.isConnected) document.documentElement.append(host);
    if (typeof host.showPopover !== 'function') return;
    host.popover = 'manual';
    if (host.matches(':popover-open')) host.hidePopover();
    host.showPopover();
  };
  let frame = null, expiry = null, last = null;
  const clear = () => {
    if (frame !== null) cancelAnimationFrame(frame);
    clearTimeout(expiry);
    frame = null; last = null;
    svg.style.visibility = label.style.visibility = 'hidden';
    return { cleared:true };
  };
  // An integration that has already resolved the element passes it as target instead of a selector.
  const mark = ({ selector, target, shape = 'rectangle', gesture = 'none',
    label: caption = '', duration = 3500, padding = 8, color = '#f97316' } = {}) => {
    if (!['rectangle','circle','none'].includes(shape)) throw Error('Unknown shape');
    if (!['wiggle','circle','none'].includes(gesture)) throw Error('Unknown gesture');
    if (!Number.isFinite(duration) || duration < 100 || duration > 15000) throw Error('Duration must be 100–15000 ms');
    if (!Number.isFinite(padding) || padding < 0 || padding > 64) throw Error('Padding must be 0–64 px');
    if (!CSS.supports('color', color)) throw Error('Invalid color');
    if (!(target instanceof Element)) {
      const matches = document.querySelectorAll(selector);
      if (matches.length !== 1) throw Error(`Expected one target, found ${matches.length}`);
      target = matches[0];
    }
    const initial = target.getBoundingClientRect();
    if (initial.width <= 0 || initial.height <= 0 || initial.bottom <= 0 || initial.top >= innerHeight
      || initial.right <= 0 || initial.left >= innerWidth) throw Error('Target is not visible in the viewport');
    clear();
    raise();
    marks.setAttribute('stroke', color);
    circle.style.display = shape === 'circle' ? '' : 'none';
    rectangle.style.display = shape === 'rectangle' ? '' : 'none';
    pointer.style.display = gesture === 'none' ? 'none' : '';
    label.textContent = String(caption);
    svg.style.visibility = 'visible';
    label.style.visibility = caption ? 'visible' : 'hidden';
    const began = performance.now();
    const draw = now => {
      if (!host.isConnected || !target.isConnected || now - began >= duration) { clear(); return; }
      const r = target.getBoundingClientRect();
      const x = r.left - padding, y = r.top - padding;
      const w = r.width + padding * 2, h = r.height + padding * 2;
      const cx = x + w/2, cy = y + h/2;
      svg.setAttribute('viewBox', `0 0 ${innerWidth} ${innerHeight}`);
      attr(circle, { cx, cy, rx: w/2 + 4, ry: h/2 + 4 });
      attr(rectangle, { x, y, width:w, height:h });
      const progress = Math.min(1, (now - began)/500);
      const outline = shape === 'circle' ? circle : rectangle;
      outline.setAttribute('pathLength', '1');
      outline.setAttribute('stroke-dasharray', '1');
      outline.setAttribute('stroke-dashoffset', String(1-progress));
      const angle = (now-began)/1600 * Math.PI*2 - Math.PI/2;
      const px = gesture === 'circle' ? cx + (w/2+14)*Math.cos(angle) : cx + 24*Math.sin(angle*2);
      const py = gesture === 'circle' ? cy + (h/2+14)*Math.sin(angle) : cy;
      pointer.setAttribute('transform', `translate(${px} ${py})`);
      label.style.left = `${Math.max(8, Math.min(x, innerWidth-label.offsetWidth-8))}px`;
      const above = y-label.offsetHeight-14, below = y+h+14;
      label.style.top = `${Math.max(8, Math.min(innerHeight-label.offsetHeight-8, above >= 8 ? above : below))}px`;
      frame = requestAnimationFrame(draw);
    };
    last = { selector, shape, gesture, duration, animatedPointer: gesture !== 'none' };
    draw(began);
    // A timer also cleans up when a background tab pauses animation frames.
    expiry = setTimeout(clear, duration);
    return { ...last, bounds: { x:initial.x,y:initial.y,width:initial.width,height:initial.height } };
  };
  const api = { mark, clear, status: () => last,
    destroy() { clear();host.remove();if (window.__walkthrough === api) delete window.__walkthrough;return { removed:true }; } };
  window.__walkthrough = api;
  clear();
  return { installed:true, shapes:['circle','rectangle'], gestures:['circle','wiggle'], syntheticPointer:true };
})();
