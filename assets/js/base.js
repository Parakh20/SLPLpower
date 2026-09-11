
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

  /* \u2500\u2500 forms: posted to /api/*, delivered by the server \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500 */
  var EMAIL = /^[^\s@,;<>"]+@[^\s@,;<>"]+\.[^\s@,;<>"]{2,}$/;
  var MAX_CV = 4 * 1024 * 1024;
  var v = function(id){ var el = document.getElementById(id); return el ? (el.value || '').trim() : ''; };
  function statusLine(id){
    var el = document.getElementById(id);
    return function(msg, ok){
      if (!el) return;
      el.textContent = msg;
      el.className = 'form-status' + (ok ? ' ok' : msg ? ' err' : '');
    };
  }
  function postForm(url, payload){
    return fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    }).then(function(r){
      return r.json().catch(function(){ return {}; }).then(function(d){
        if (!r.ok) throw new Error(d.error || 'Could not send right now.');
        return d;
      });
    });
  }
  function readBase64(file){
    return new Promise(function(resolve, reject){
      var fr = new FileReader();
      fr.onload = function(){ resolve(String(fr.result).split(',')[1] || ''); };
      fr.onerror = function(){ reject(new Error('Your CV could not be read. Please attach it again.')); };
      fr.readAsDataURL(file);
    });
  }

  /* enquiry -> /api/enquiry: info@slplpower.com, careers questions to hr@ */
  var send = document.getElementById('send');
  if (send) send.addEventListener('click', function(){
    var say = statusLine('fs');

    if (!v('nm')) { say('Please enter your name.'); return; }
    if (!EMAIL.test(v('em'))) { say('Please enter a valid email address.'); return; }
    if (v('ms').length < 10) { say('Please describe the scope in a little more detail.'); return; }

    send.disabled = true;
    say('Sending\u2026');

    postForm('/api/enquiry', {
      name: v('nm'), organisation: v('org'), email: v('em'), phone: v('ph'),
      service: document.getElementById('sv').value, message: v('ms'),
      website: v('wb')
    }).then(function(){
      say('Thank you \u2014 your enquiry is with us. We reply within one working day.', true);
      ['nm','org','em','ph','ms'].forEach(function(id){ document.getElementById(id).value = ''; });
    }).catch(function(err){
      say(err.message + ' You can also email info@slplpower.com directly.');
    }).then(function(){
      send.disabled = false;
    });
  });

  /* application -> /api/apply: hr@slplpower.com with the CV attached */
  var applyBtn = document.getElementById('apply-send');
  if (applyBtn){
    var role = document.getElementById('ap-role');
    document.querySelectorAll('a[data-role]').forEach(function(a){
      a.addEventListener('click', function(){ role.value = a.dataset.role; });
    });

    applyBtn.addEventListener('click', function(){
      var say = statusLine('ap-fs');
      var cvInput = document.getElementById('ap-cv');
      var file = cvInput.files && cvInput.files[0];

      if (!v('ap-nm')) { say('Please enter your name.'); return; }
      if (!EMAIL.test(v('ap-em'))) { say('Please enter a valid email address.'); return; }
      if (!file) { say('Please attach your CV (PDF or Word).'); return; }
      if (!/\.(pdf|docx?)$/i.test(file.name)) { say('Your CV must be a PDF or Word document.'); return; }
      if (file.size > MAX_CV) { say('Your CV is over 4 MB. Please send a smaller file.'); return; }

      applyBtn.disabled = true;
      say('Sending your application\u2026');

      readBase64(file).then(function(data){
        return postForm('/api/apply', {
          name: v('ap-nm'), email: v('ap-em'), phone: v('ap-ph'),
          role: role.value, message: v('ap-ms'), website: v('ap-wb'),
          cv: { name: file.name, data: data }
        });
      }).then(function(){
        say('Thank you \u2014 your application and CV are with our HR team.', true);
        ['ap-nm','ap-em','ap-ph','ap-ms'].forEach(function(id){ document.getElementById(id).value = ''; });
        cvInput.value = '';
      }).catch(function(err){
        say(err.message + ' You can also email your CV to hr@slplpower.com.');
      }).then(function(){
        applyBtn.disabled = false;
      });
    });
  }

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
