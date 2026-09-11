
(function(){
  var reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  document.getElementById('yr').textContent = new Date().getFullYear();

  /* nav */
  var nav = document.getElementById('nav'), burger = document.getElementById('burger');
  addEventListener('scroll', function(){ nav.classList.toggle('stuck', scrollY > 40); }, {passive:true});
  var scrim = document.getElementById('scrim');
  function setMenu(open){
    nav.classList.toggle('open', open);
    document.body.classList.toggle('menu-open', open);
    burger.setAttribute('aria-expanded', open);
  }
  burger.addEventListener('click', function(){ setMenu(!nav.classList.contains('open')); });
  scrim.addEventListener('click', function(){ setMenu(false); });
  addEventListener('keydown', function(e){ if (e.key === 'Escape') setMenu(false); });
  document.getElementById('links').addEventListener('click', function(e){
    if (e.target.tagName === 'A') setMenu(false);
  });
  /* services dropdown: hover on desktop, tap on touch devices */
  document.querySelectorAll('.has-sub').forEach(function(d){
    d.querySelector('a').addEventListener('click', function(e){
      if (matchMedia('(hover: none)').matches && !d.classList.contains('open')){
        e.preventDefault(); d.classList.add('open');
      }
    });
  });

  var mq = matchMedia('(min-width: 861px)');
  (mq.addEventListener ? mq.addEventListener.bind(mq,'change') : mq.addListener.bind(mq))(function(){
    if (mq.matches) setMenu(false);
  });

  /* scroll reveal */
  var io = new IntersectionObserver(function(es){
    es.forEach(function(e){ if (e.isIntersecting){ e.target.classList.add('revealed'); io.unobserve(e.target); } });
  }, {threshold:.12, rootMargin:'0px 0px -8% 0px'});
  document.querySelectorAll('.rv,.stg').forEach(function(el){ io.observe(el); });

  /* card tilt */
  if (!reduce && matchMedia('(hover: hover)').matches){
    document.querySelectorAll('.tilt').forEach(function(c){
      c.addEventListener('mousemove', function(e){
        var r = c.getBoundingClientRect();
        var x = (e.clientX - r.left) / r.width - .5, y = (e.clientY - r.top) / r.height - .5;
        c.style.transform = 'perspective(900px) rotateX(' + (-y*5).toFixed(2) + 'deg) rotateY(' + (x*5).toFixed(2) + 'deg) translateY(-6px)';
      });
      c.addEventListener('mouseleave', function(){ c.style.transform = ''; });
    });
  }

  /* project filter — only present on pages that list projects */
  var filters = document.getElementById('filters'), cards = document.querySelectorAll('#grid .proj');
  if (filters) filters.addEventListener('click', function(e){
    var b = e.target.closest('button'); if (!b) return;
    filters.querySelectorAll('button').forEach(function(x){ x.classList.remove('on'); });
    b.classList.add('on');
    var f = b.dataset.f;
    cards.forEach(function(c){ c.classList.toggle('hide', f !== 'all' && c.dataset.c !== f); });
  });

  /* enquiry -> /api/enquiry, delivered to info@slplpower.com */
  var send = document.getElementById('send');
  if (send) send.addEventListener('click', function(){
    var v = function(id){ return (document.getElementById(id).value || '').trim(); };
    var status = document.getElementById('fs');
    var say = function(msg, ok){
      if (!status) return;
      status.textContent = msg;
      status.className = 'form-status' + (ok ? ' ok' : msg ? ' err' : '');
    };

    if (!v('nm')) { say('Please enter your name.'); return; }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(v('em'))) {
      say('Please enter a valid email address.'); return;
    }
    if (v('ms').length < 10) { say('Please describe the scope in a little more detail.'); return; }

    send.disabled = true;
    say('Sending\u2026');

    fetch('/api/enquiry', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: v('nm'), organisation: v('org'), email: v('em'), phone: v('ph'),
        service: document.getElementById('sv').value, message: v('ms'),
        website: v('wb')
      })
    }).then(function(r){
      return r.json().catch(function(){ return {}; }).then(function(d){
        if (!r.ok) throw new Error(d.error || 'Could not send right now.');
        return d;
      });
    }).then(function(){
      say('Thank you \u2014 your enquiry is with us. We reply within one working day.', true);
      ['nm','org','em','ph','ms'].forEach(function(id){ document.getElementById(id).value = ''; });
    }).catch(function(err){
      say(err.message + ' You can also email info@slplpower.com directly.');
    }).then(function(){
      send.disabled = false;
    });
  });

  /* ── gallery: category filter + lightbox ──────────────────────── */
  var gal = document.getElementById('gal');
  if (gal){
    var gfilters = document.getElementById('gfilters');
    var tiles = [].slice.call(gal.querySelectorAll('.tile'));
    var shots = tiles.filter(function(t){ return !t.classList.contains('empty'); });

    if (gfilters) gfilters.addEventListener('click', function(e){
      var btn = e.target.closest('button'); if (!btn) return;
      gfilters.querySelectorAll('button').forEach(function(x){ x.classList.remove('on'); });
      btn.classList.add('on');
      var f = btn.dataset.f;
      tiles.forEach(function(t){ t.classList.toggle('hide', f !== 'all' && t.dataset.c !== f); });
    });

    var lb = document.getElementById('lb');
    if (lb && shots.length){
      var lbImg = lb.querySelector('img'),
          lbCap = lb.querySelector('figcaption'),
          lbNum = lb.querySelector('.lb-count'),
          idx = 0;

      function visible(){
        return shots.filter(function(t){ return !t.classList.contains('hide'); });
      }
      function show(i){
        var list = visible(); if (!list.length) return;
        idx = (i + list.length) % list.length;
        var t = list[idx];
        lbImg.src = t.dataset.full;
        lbImg.alt = t.dataset.caption || '';
        lbCap.innerHTML = (t.dataset.caption || '') +
          (t.dataset.meta ? '<span>' + t.dataset.meta + '</span>' : '');
        lbNum.textContent = (idx + 1) + ' / ' + list.length;
      }
      function open(t){
        show(visible().indexOf(t));
        lb.classList.add('on');
        document.body.classList.add('menu-open');
        lb.querySelector('.lb-close').focus();
      }
      function close(){
        lb.classList.remove('on');
        document.body.classList.remove('menu-open');
      }
      shots.forEach(function(t){ t.addEventListener('click', function(){ open(t); }); });
      lb.querySelector('.lb-close').addEventListener('click', close);
      lb.querySelector('.lb-prev').addEventListener('click', function(e){ e.stopPropagation(); show(idx - 1); });
      lb.querySelector('.lb-next').addEventListener('click', function(e){ e.stopPropagation(); show(idx + 1); });
      lb.addEventListener('click', function(e){ if (e.target === lb) close(); });
      addEventListener('keydown', function(e){
        if (!lb.classList.contains('on')) return;
        if (e.key === 'Escape') close();
        if (e.key === 'ArrowLeft') show(idx - 1);
        if (e.key === 'ArrowRight') show(idx + 1);
      });
      /* swipe on touch */
      var x0 = null;
      lb.addEventListener('touchstart', function(e){ x0 = e.touches[0].clientX; }, {passive:true});
      lb.addEventListener('touchend', function(e){
        if (x0 === null) return;
        var dx = e.changedTouches[0].clientX - x0;
        if (Math.abs(dx) > 50) show(idx + (dx < 0 ? 1 : -1));
        x0 = null;
      }, {passive:true});
    }
  }
})();
