// Careers application handler. Relays the application to hr@slplpower.com
// with the candidate's CV attached.
//
// The browser sends the CV as base64 inside the JSON body. It is accepted only
// as PDF, DOC or DOCX, up to MAX_CV_BYTES, and only when the file's leading
// bytes match its extension, so a renamed executable is refused.
//
// Optional override (Vercel project settings):
//   CAREERS_TO  default hr@slplpower.com
// Delivery settings live in ./_lib/mail.js.

const {
  MAX_FIELD,
  MAX_MESSAGE,
  clean,
  cleanText,
  isEmail,
  renderText,
  renderHtml,
  createHandler,
} = require('./_lib/mail');

const TO = process.env.CAREERS_TO || 'hr@slplpower.com';

const GENERAL = 'General application';
const ROLES = [
  'Testing & Commissioning Engineer',
  'O&M Engineer / Shift Engineer',
  'Protection & Power System Studies Engineer',
  'Field Technician',
  GENERAL,
];

// Vercel refuses request bodies over 4.5 MB (FUNCTION_PAYLOAD_TOO_LARGE), and
// base64 adds a third, so 3 MB is the largest file that reliably fits.
const MAX_CV_BYTES = 3 * 1024 * 1024;
const CV_FORMATS = {
  pdf: '25504446', // %PDF
  docx: '504b0304', // zip container
  doc: 'd0cf11e0', // OLE compound file
};
const BASE64 = /^[A-Za-z0-9+/]+={0,2}$/;

const NOT_A_CV = 'Your CV must be a PDF or Word document.';
const UNREADABLE = 'Your CV could not be read. Please attach it again.';

function formatSize(bytes) {
  return bytes >= 1024 * 1024
    ? (bytes / (1024 * 1024)).toFixed(1) + ' MB'
    : Math.max(1, Math.round(bytes / 1024)) + ' KB';
}

function validateCv(cv) {
  if (!cv || typeof cv !== 'object') return { error: 'Please attach your CV (PDF or Word).' };

  const original = clean(cv.name, MAX_FIELD);
  const ext = ((original.match(/\.([a-z0-9]+)$/i) || [])[1] || '').toLowerCase();
  if (!CV_FORMATS[ext]) return { error: NOT_A_CV };

  const data = typeof cv.data === 'string' ? cv.data.replace(/^data:[^,]*,/, '') : '';
  if (!BASE64.test(data)) return { error: UNREADABLE };

  const bytes = Buffer.from(data, 'base64');
  if (bytes.length === 0) return { error: UNREADABLE };
  if (bytes.length > MAX_CV_BYTES) return { error: 'Your CV is over 3 MB. Please send a smaller file.' };
  if (bytes.subarray(0, 4).toString('hex') !== CV_FORMATS[ext]) return { error: NOT_A_CV };
  // Every ZIP-based format (xlsx, zip, apk...) shares the DOCX header; only a
  // Word document names a word/ folder inside it.
  if (ext === 'docx' && !bytes.includes('word/')) return { error: NOT_A_CV };

  const stem = original
    .slice(0, -(ext.length + 1))
    .replace(/[^\w\- ]+/g, '_')
    .trim()
    .slice(0, 80);
  return {
    cv: {
      filename: (stem || 'CV') + '.' + ext,
      content: bytes.toString('base64'),
      size: bytes.length,
    },
  };
}

function validate(body) {
  const name = clean(body.name, MAX_FIELD);
  const email = clean(body.email, MAX_FIELD);

  if (!name) return { error: 'Please enter your name.' };
  if (!isEmail(email)) return { error: 'Please enter a valid email address.' };

  const { error, cv } = validateCv(body.cv);
  if (error) return { error };

  const role = clean(body.role, MAX_FIELD);
  return {
    data: {
      name,
      email,
      cv,
      phone: clean(body.phone, MAX_FIELD),
      role: ROLES.includes(role) ? role : GENERAL,
      note: cleanText(body.message, MAX_MESSAGE),
    },
  };
}

function compose(application) {
  const rows = [
    ['Name', application.name],
    ['Email', application.email],
    ['Phone', application.phone],
    ['Role', application.role],
    ['CV', application.cv.filename + ' (' + formatSize(application.cv.size) + ', attached)'],
  ];
  return {
    to: TO,
    replyTo: application.email,
    subject: 'Job application - ' + application.role + ' - ' + application.name,
    text: renderText(rows, 'Note from the candidate', application.note),
    html: renderHtml('New job application', rows, 'Note from the candidate', application.note),
    attachments: [{ filename: application.cv.filename, content: application.cv.content }],
  };
}

module.exports = createHandler({ validate, compose, fallbackAddress: TO });
module.exports.validate = validate;
module.exports.validateCv = validateCv;
module.exports.compose = compose;
module.exports.MAX_CV_BYTES = MAX_CV_BYTES;
