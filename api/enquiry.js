// Contact-form handler. Receives the enquiry form POST and relays it to
// info@slplpower.com through Resend. No dependencies: Resend's REST API is
// called directly with the runtime's global fetch.
//
// Required environment variable (set in Vercel project settings):
//   RESEND_API_KEY
// Optional overrides:
//   ENQUIRY_TO    default info@slplpower.com
//   ENQUIRY_FROM  default "SLPL Website <website@send.slplpower.com>"

const TO = process.env.ENQUIRY_TO || 'info@slplpower.com';
const FROM = process.env.ENQUIRY_FROM || 'SLPL Website <website@send.slplpower.com>';

const MAX_FIELD = 200;
const MAX_MESSAGE = 4000;

const SERVICES = [
  'Testing & Commissioning',
  'Operation & Maintenance',
  'Power System Studies',
  'Careers',
  'Something else',
];

// Strip control characters so a crafted value cannot inject header-like lines.
const CONTROL_CHARS = /[\u0000-\u001f\u007f]/g;

function clean(value, limit) {
  if (typeof value !== 'string') return '';
  return value.replace(CONTROL_CHARS, ' ').trim().slice(0, limit);
}

function escapeHtml(value) {
  return value
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function validate(body) {
  const name = clean(body.name, MAX_FIELD);
  const email = clean(body.email, MAX_FIELD);
  const message = clean(body.message, MAX_MESSAGE);

  if (!name) return { error: 'Please enter your name.' };
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email)) {
    return { error: 'Please enter a valid email address.' };
  }
  if (message.length < 10) {
    return { error: 'Please describe the scope in a little more detail.' };
  }

  const service = clean(body.service, MAX_FIELD);
  return {
    enquiry: {
      name,
      email,
      message,
      organisation: clean(body.organisation, MAX_FIELD),
      phone: clean(body.phone, MAX_FIELD),
      service: SERVICES.includes(service) ? service : 'Something else',
    },
  };
}

function buildRows(enquiry) {
  return [
    ['Name', enquiry.name],
    ['Organisation', enquiry.organisation || '-'],
    ['Email', enquiry.email],
    ['Phone', enquiry.phone || '-'],
    ['Service', enquiry.service],
  ];
}

function textBody(enquiry) {
  const rows = buildRows(enquiry)
    .map(([label, value]) => label + ': ' + value)
    .join('\n');
  return rows + '\n\nScope\n-----\n' + enquiry.message + '\n';
}

function htmlBody(enquiry) {
  const rows = buildRows(enquiry)
    .map(
      ([label, value]) =>
        '<tr><td style="padding:4px 16px 4px 0;color:#5b6472">' + label + '</td>' +
        '<td style="padding:4px 0"><strong>' + escapeHtml(value) + '</strong></td></tr>'
    )
    .join('');
  return (
    '<div style="font:15px/1.6 -apple-system,Segoe UI,Roboto,sans-serif;color:#1b2230">' +
    '<h2 style="margin:0 0 16px;font-size:17px">New website enquiry</h2>' +
    '<table style="border-collapse:collapse;margin-bottom:20px">' + rows + '</table>' +
    '<h3 style="margin:0 0 6px;font-size:14px;color:#5b6472">Scope</h3>' +
    '<div style="white-space:pre-wrap">' + escapeHtml(enquiry.message) + '</div>' +
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

module.exports = async function handler(req, res) {
  if (req.method !== 'POST') {
    res.setHeader('Allow', 'POST');
    return res.status(405).json({ error: 'Method not allowed.' });
  }

  if (!process.env.RESEND_API_KEY) {
    console.error('RESEND_API_KEY is not configured');
    return res.status(500).json({ error: 'Enquiry form is not configured yet.' });
  }

  let body;
  try {
    body = await readBody(req);
  } catch {
    return res.status(400).json({ error: 'Malformed request.' });
  }

  // Honeypot: bots fill every field they find, humans never see this one.
  if (clean(body.website, MAX_FIELD)) {
    return res.status(200).json({ ok: true });
  }

  const { error, enquiry } = validate(body);
  if (error) return res.status(400).json({ error });

  let response;
  try {
    response = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: {
        Authorization: 'Bearer ' + process.env.RESEND_API_KEY,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        from: FROM,
        to: [TO],
        reply_to: enquiry.email,
        subject: 'Website enquiry - ' + enquiry.service + ' - ' + enquiry.name,
        text: textBody(enquiry),
        html: htmlBody(enquiry),
      }),
    });
  } catch (err) {
    console.error('Resend request failed', err);
    return res
      .status(502)
      .json({ error: 'Could not send right now. Please email info@slplpower.com.' });
  }

  if (!response.ok) {
    console.error('Resend rejected the message', response.status, await response.text());
    return res
      .status(502)
      .json({ error: 'Could not send right now. Please email info@slplpower.com.' });
  }

  return res.status(200).json({ ok: true });
};
