// Contact-form handler. Relays the enquiry to info@slplpower.com, except
// careers questions, which go to the HR mailbox.
//
// Optional overrides (Vercel project settings):
//   ENQUIRY_TO  default info@slplpower.com
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

const INFO_TO = process.env.ENQUIRY_TO || 'info@slplpower.com';
const HR_TO = process.env.CAREERS_TO || 'hr@slplpower.com';

const SERVICES = [
  'Testing & Commissioning',
  'Operation & Maintenance',
  'Power System Studies',
  'Careers',
  'Something else',
];

function recipientFor(service) {
  return service === 'Careers' ? HR_TO : INFO_TO;
}

function validate(body) {
  const name = clean(body.name, MAX_FIELD);
  const email = clean(body.email, MAX_FIELD);
  const message = cleanText(body.message, MAX_MESSAGE);

  if (!name) return { error: 'Please enter your name.' };
  if (!isEmail(email)) return { error: 'Please enter a valid email address.' };
  if (message.length < 10) {
    return { error: 'Please describe the scope in a little more detail.' };
  }

  const service = clean(body.service, MAX_FIELD);
  return {
    data: {
      name,
      email,
      message,
      organisation: clean(body.organisation, MAX_FIELD),
      phone: clean(body.phone, MAX_FIELD),
      service: SERVICES.includes(service) ? service : 'Something else',
    },
  };
}

function compose(enquiry) {
  const rows = [
    ['Name', enquiry.name],
    ['Organisation', enquiry.organisation],
    ['Email', enquiry.email],
    ['Phone', enquiry.phone],
    ['Service', enquiry.service],
  ];
  return {
    to: recipientFor(enquiry.service),
    replyTo: enquiry.email,
    subject: 'Website enquiry - ' + enquiry.service + ' - ' + enquiry.name,
    text: renderText(rows, 'Scope', enquiry.message),
    html: renderHtml('New website enquiry', rows, 'Scope', enquiry.message),
  };
}

module.exports = createHandler({ validate, compose, fallbackAddress: INFO_TO });
module.exports.validate = validate;
module.exports.compose = compose;
module.exports.recipientFor = recipientFor;
