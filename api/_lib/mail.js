// Shared plumbing for the form handlers in /api. The leading underscore keeps
// Vercel from exposing this folder as a route.
//
// Mail goes out through Resend's REST API with the runtime's global fetch, so
// there are no dependencies. Required environment variable:
//   RESEND_API_KEY
// Optional override:
//   MAIL_FROM  default "SLPL Website <website@send.slplpower.com>"

const RESEND_URL = 'https://api.resend.com/emails';
const DEFAULT_FROM = 'SLPL Website <website@send.slplpower.com>';

const MAX_FIELD = 200;
const MAX_MESSAGE = 4000;

// No commas, semicolons or angle brackets: the address becomes reply_to, and a
// list separator there would turn one sender into several recipients.
const EMAIL = /^[^\s@,;<>"]+@[^\s@,;<>"]+\.[^\s@,;<>"]{2,}$/;
// Single-line fields lose every control character, so a crafted value cannot
// inject header-like lines. Free text keeps tabs and line breaks.
const charRange = (from, to) => String.fromCharCode(from) + '-' + String.fromCharCode(to);
const DEL = String.fromCharCode(127);
const CONTROL_CHARS = new RegExp('[' + charRange(0, 31) + DEL + ']', 'g');
const CONTROL_CHARS_EXCEPT_BREAKS = new RegExp('[' + charRange(0, 8) + charRange(11, 31) + DEL + ']', 'g');

function clean(value, limit) {
  if (typeof value !== 'string') return '';
  return value.replace(CONTROL_CHARS, ' ').trim().slice(0, limit);
}

function cleanText(value, limit) {
  if (typeof value !== 'string') return '';
  return value.replace(/\r\n?/g, '\n').replace(CONTROL_CHARS_EXCEPT_BREAKS, ' ').trim().slice(0, limit);
}

function isEmail(value) {
  return EMAIL.test(value);
}

function escapeHtml(value) {
  return value
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

// rows: [[label, value], ...]; the free-text block is optional.
function renderText(rows, heading, message) {
  const table = rows.map(([label, value]) => label + ': ' + (value || '-')).join('\n');
  if (!message) return table + '\n';
  return table + '\n\n' + heading + '\n' + '-'.repeat(heading.length) + '\n' + message + '\n';
}

function renderHtml(title, rows, heading, message) {
  const table = rows
    .map(
      ([label, value]) =>
        '<tr><td style="padding:4px 16px 4px 0;color:#5b6472">' + label + '</td>' +
        '<td style="padding:4px 0"><strong>' + escapeHtml(value || '-') + '</strong></td></tr>'
    )
    .join('');
  const block = message
    ? '<h3 style="margin:0 0 6px;font-size:14px;color:#5b6472">' + heading + '</h3>' +
      '<div style="white-space:pre-wrap">' + escapeHtml(message) + '</div>'
    : '';
  return (
    '<div style="font:15px/1.6 -apple-system,Segoe UI,Roboto,sans-serif;color:#1b2230">' +
    '<h2 style="margin:0 0 16px;font-size:17px">' + title + '</h2>' +
    '<table style="border-collapse:collapse;margin-bottom:20px">' + table + '</table>' +
    block +
    '</div>'
  );
}

async function readBody(req) {
  if (req.body && typeof req.body === 'object') return req.body;
  if (typeof req.body === 'string') return JSON.parse(req.body);

  const chunks = [];
  for await (const chunk of req) chunks.push(chunk);
  return JSON.parse(Buffer.concat(chunks).toString('utf8') || '{}');
}

async function sendMail({ to, replyTo, subject, text, html, attachments }) {
  const payload = {
    from: process.env.MAIL_FROM || DEFAULT_FROM,
    to: [to],
    reply_to: replyTo,
    subject,
    text,
    html,
  };
  if (attachments && attachments.length) payload.attachments = attachments;

  const response = await fetch(RESEND_URL, {
    method: 'POST',
    headers: {
      Authorization: 'Bearer ' + process.env.RESEND_API_KEY,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    throw new Error('Resend rejected the message: ' + response.status + ' ' + (await response.text()));
  }
}

// Wraps the request plumbing every form shares: method check, configuration
// check, body parsing, honeypot, validation and delivery.
//   validate(body) -> { error } | { data }
//   compose(data)  -> { to, replyTo, subject, text, html, attachments? }
function createHandler({ validate, compose, fallbackAddress }) {
  const failure = 'Could not send right now. Please email ' + fallbackAddress + '.';

  return async function handler(req, res) {
    if (req.method !== 'POST') {
      res.setHeader('Allow', 'POST');
      return res.status(405).json({ error: 'Method not allowed.' });
    }

    if (!process.env.RESEND_API_KEY) {
      console.error('RESEND_API_KEY is not configured');
      return res.status(500).json({ error: 'This form is not configured yet.' });
    }

    let body;
    try {
      body = await readBody(req);
    } catch {
      return res.status(400).json({ error: 'Malformed request.' });
    }
    if (!body || typeof body !== 'object') {
      return res.status(400).json({ error: 'Malformed request.' });
    }

    // Honeypot: bots fill every field they find, humans never see this one.
    if (clean(body.website, MAX_FIELD)) {
      return res.status(200).json({ ok: true });
    }

    const { error, data } = validate(body);
    if (error) return res.status(400).json({ error });

    try {
      await sendMail(compose(data));
    } catch (err) {
      console.error('Mail delivery failed:', err.message);
      return res.status(502).json({ error: failure });
    }

    return res.status(200).json({ ok: true });
  };
}

module.exports = {
  MAX_FIELD,
  MAX_MESSAGE,
  clean,
  cleanText,
  isEmail,
  escapeHtml,
  renderText,
  renderHtml,
  readBody,
  sendMail,
  createHandler,
};
