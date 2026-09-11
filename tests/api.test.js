// Tests for the /api form handlers. No dependencies: run with
//   node --test 'tests/*.test.js'
// Resend is never called; global fetch is replaced with a recorder.

const test = require('node:test');
const assert = require('node:assert/strict');

process.env.RESEND_API_KEY = 'test-key';

const enquiry = require('../api/enquiry');
const apply = require('../api/apply');
const { cleanText, renderText } = require('../api/_lib/mail');

const b64 = (s) => Buffer.from(s).toString('base64');
const PDF = b64('%PDF-1.7 fake resume');
const ZIP_HEADER = Buffer.from([0x50, 0x4b, 0x03, 0x04]);
const DOCX = Buffer.concat([ZIP_HEADER, Buffer.from('word/document.xml')]).toString('base64');
const PLAIN_ZIP = Buffer.concat([ZIP_HEADER, Buffer.from('payload.exe')]).toString('base64');

function mockRes() {
  return {
    statusCode: 200,
    headers: {},
    body: undefined,
    setHeader(k, v) { this.headers[k] = v; },
    status(code) { this.statusCode = code; return this; },
    json(obj) { this.body = obj; return this; },
  };
}

// Replaces global fetch for one test and returns the captured Resend payloads.
function stubFetch(t, { ok = true, status = 200 } = {}) {
  const sent = [];
  const original = global.fetch;
  global.fetch = async (url, opts) => {
    sent.push({ url, payload: JSON.parse(opts.body), headers: opts.headers });
    return { ok, status, text: async () => 'rejected' };
  };
  t.after(() => { global.fetch = original; });
  return sent;
}

async function post(handler, body) {
  const res = mockRes();
  await handler({ method: 'POST', body }, res);
  return res;
}

const goodEnquiry = {
  name: 'Asha Rao', email: 'asha@example.com', organisation: 'GridCo',
  phone: '+91 99999 00000', service: 'Testing & Commissioning',
  message: '765 kV GIS, two bays.\nTarget: March.',
};

const goodApplication = {
  name: 'Ravi Patel', email: 'ravi@example.com', phone: '+91 98765 43210',
  role: 'Field Technician', message: 'Five years in substations.\nBased in Vadodara.',
  cv: { name: 'Ravi Patel CV.pdf', data: PDF },
};

// ── shared helpers ────────────────────────────────────────────────
test('cleanText keeps line breaks but strips other control characters', () => {
  const bell = String.fromCharCode(7);
  assert.equal(cleanText('line one' + bell + '\r\nline two', 100), 'line one \nline two');
});

test('renderText omits the free-text block when there is no message', () => {
  assert.equal(renderText([['Name', 'A'], ['Phone', '']], 'Note', ''), 'Name: A\nPhone: -\n');
});

// ── enquiry ───────────────────────────────────────────────────────
test('enquiry routes Careers to HR and every other service to info', () => {
  assert.equal(enquiry.recipientFor('Careers'), 'hr@slplpower.com');
  assert.equal(enquiry.recipientFor('Testing & Commissioning'), 'info@slplpower.com');
  assert.equal(enquiry.recipientFor('Something else'), 'info@slplpower.com');
});

test('enquiry validation rejects a missing name, a bad email and a short scope', () => {
  assert.match(enquiry.validate({ ...goodEnquiry, name: ' ' }).error, /name/);
  assert.match(enquiry.validate({ ...goodEnquiry, email: 'nope' }).error, /email/);
  assert.match(enquiry.validate({ ...goodEnquiry, message: 'short' }).error, /detail/);
});

test('enquiry validation maps an unknown service to "Something else"', () => {
  assert.equal(enquiry.validate({ ...goodEnquiry, service: 'Hacking' }).data.service, 'Something else');
});

test('a normal enquiry is delivered to info@ with line breaks intact', async (t) => {
  const sent = stubFetch(t);
  const res = await post(enquiry, goodEnquiry);

  assert.equal(res.statusCode, 200);
  assert.equal(sent.length, 1);
  assert.deepEqual(sent[0].payload.to, ['info@slplpower.com']);
  assert.equal(sent[0].payload.reply_to, 'asha@example.com');
  assert.match(sent[0].payload.text, /two bays\.\nTarget: March\./);
  assert.equal(sent[0].payload.attachments, undefined);
});

test('a Careers enquiry is delivered to hr@', async (t) => {
  const sent = stubFetch(t);
  await post(enquiry, { ...goodEnquiry, service: 'Careers' });
  assert.deepEqual(sent[0].payload.to, ['hr@slplpower.com']);
});

// ── apply: CV checks ──────────────────────────────────────────────
test('CV is required', () => {
  assert.match(apply.validate({ ...goodApplication, cv: undefined }).error, /attach your CV/);
});

test('CV with a non-document extension is refused', () => {
  const cv = { name: 'resume.exe', data: PDF };
  assert.match(apply.validateCv(cv).error, /PDF or Word/);
});

test('CV whose bytes do not match its extension is refused', () => {
  const cv = { name: 'resume.pdf', data: b64('MZ this is an executable') };
  assert.match(apply.validateCv(cv).error, /PDF or Word/);
});

test('a plain ZIP renamed to .docx is refused', () => {
  assert.match(apply.validateCv({ name: 'resume.docx', data: PLAIN_ZIP }).error, /PDF or Word/);
});

test('an email containing a list separator is refused', () => {
  assert.match(apply.validate({ ...goodApplication, email: 'a,b@example.com' }).error, /email/);
  assert.match(enquiry.validate({ ...goodEnquiry, email: 'a;b@example.com' }).error, /email/);
});

test('CV that is not valid base64 is refused', () => {
  assert.match(apply.validateCv({ name: 'cv.pdf', data: 'not base64!!' }).error, /could not be read/);
});

test('CV over the size limit is refused', () => {
  const big = Buffer.alloc(apply.MAX_CV_BYTES + 1);
  big.write('%PDF');
  const cv = { name: 'cv.pdf', data: big.toString('base64') };
  assert.match(apply.validateCv(cv).error, /over 4 MB/);
});

test('DOCX CV is accepted, a data-URL prefix is stripped, the filename is sanitised', () => {
  const { cv } = apply.validateCv({ name: '../../My<CV>.DOCX', data: 'data:application/zip;base64,' + DOCX });
  assert.equal(cv.filename, '_My_CV_.docx');
  assert.equal(cv.content, DOCX);
});

test('application validation maps an unknown role to General application', () => {
  assert.equal(apply.validate({ ...goodApplication, role: 'CEO' }).data.role, 'General application');
});

// ── apply: delivery ───────────────────────────────────────────────
test('an application is delivered to hr@ with the CV attached', async (t) => {
  const sent = stubFetch(t);
  const res = await post(apply, goodApplication);

  assert.equal(res.statusCode, 200);
  const mail = sent[0].payload;
  assert.deepEqual(mail.to, ['hr@slplpower.com']);
  assert.equal(mail.reply_to, 'ravi@example.com');
  assert.equal(mail.subject, 'Job application - Field Technician - Ravi Patel');
  assert.deepEqual(mail.attachments, [{ filename: 'Ravi Patel CV.pdf', content: PDF }]);
  assert.match(mail.text, /CV: Ravi Patel CV\.pdf \(1 KB, attached\)/);
  assert.match(mail.text, /Five years in substations\.\nBased in Vadodara\./);
});

test('an invalid application is rejected before anything is sent', async (t) => {
  const sent = stubFetch(t);
  const res = await post(apply, { ...goodApplication, cv: { name: 'cv.txt', data: PDF } });
  assert.equal(res.statusCode, 400);
  assert.equal(sent.length, 0);
});

// ── shared handler behaviour ──────────────────────────────────────
test('honeypot submissions get a fake success and send nothing', async (t) => {
  const sent = stubFetch(t);
  const res = await post(apply, { ...goodApplication, website: 'spam.example' });
  assert.equal(res.statusCode, 200);
  assert.equal(sent.length, 0);
});

test('GET is refused with 405', async () => {
  const res = mockRes();
  await enquiry({ method: 'GET' }, res);
  assert.equal(res.statusCode, 405);
  assert.equal(res.headers.Allow, 'POST');
});

test('a malformed JSON body is refused with 400', async () => {
  const res = await post(enquiry, '{not json');
  assert.equal(res.statusCode, 400);
});

test('a Resend rejection becomes a 502 naming the fallback mailbox', async (t) => {
  stubFetch(t, { ok: false, status: 422 });
  const original = console.error;
  console.error = () => {};
  t.after(() => { console.error = original; });

  const res = await post(apply, goodApplication);
  assert.equal(res.statusCode, 502);
  assert.match(res.body.error, /hr@slplpower\.com/);
});

test('a missing API key is reported as not configured', async (t) => {
  const key = process.env.RESEND_API_KEY;
  delete process.env.RESEND_API_KEY;
  const original = console.error;
  console.error = () => {};
  t.after(() => { process.env.RESEND_API_KEY = key; console.error = original; });

  const res = await post(enquiry, goodEnquiry);
  assert.equal(res.statusCode, 500);
});
