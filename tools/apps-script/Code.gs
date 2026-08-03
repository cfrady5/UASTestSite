/**
 * Midwest UAS Test Site — inquiry form endpoint
 * =============================================
 * A Google Apps Script web app that receives the landing page's inquiry form and
 * emails it to the shared inbox. Mail is sent by your own Google Workspace tenant,
 * so no third-party service ever sees an inquirer's details.
 *
 * Deployment steps are in the repository README, under
 * "Making it deliver to the shared inbox".
 *
 * Two things worth knowing before editing:
 *
 *  1. The page posts with Content-Type: text/plain, not application/json. That is
 *     deliberate — an application/json POST is preflighted, and Apps Script does not
 *     answer OPTIONS requests, so it would fail before arriving. The body is still
 *     JSON; only the declared type differs, and JSON.parse below is unaffected.
 *
 *  2. Apps Script cannot return a non-200 HTTP status. Failures are signalled with
 *     { ok: false } in the body, which the page checks for. Do not "simplify" that
 *     away or the visitor gets a success message for a mail that never sent.
 */

// The shared inbox that receives every inquiry.
var TO = 'MidwestUASTestSite@theari.us';

// Shown as the sender's display name on the delivered mail.
var FROM_NAME = 'Midwest UAS Test Site website';

function doPost(e) {
  try {
    if (!e || !e.postData || !e.postData.contents) {
      return respond({ ok: false, error: 'Empty request body' });
    }

    var data = JSON.parse(e.postData.contents);

    // Honeypot. The page filters these already; this is the server-side backstop
    // for anything posting straight at this URL. Answer as though it succeeded so
    // the sender learns nothing, but send no mail.
    if (data.website) {
      return respond({ ok: true });
    }

    var name    = String(data.name    || '').trim();
    var email   = String(data.email   || '').trim();
    var message = String(data.message || '').trim();

    if (!name || !email || !message) {
      return respond({ ok: false, error: 'Missing required fields' });
    }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email)) {
      return respond({ ok: false, error: 'Invalid email address' });
    }

    var body = [
      'A new inquiry was submitted from the Midwest UAS Test Site website.',
      '',
      'Name:             ' + name,
      'Email:            ' + email,
      'Organization:     ' + (String(data.organization || '').trim() || '—'),
      'Area of interest: ' + (String(data.interest || '').trim() || '—'),
      '',
      '-----------------------------------------',
      '',
      message,
      '',
      '-----------------------------------------',
      'Reply directly to this message to respond to the sender.'
    ].join('\n');

    MailApp.sendEmail({
      to:      TO,
      subject: String(data.subject || 'Test Site Inquiry — ' + name),
      body:    body,
      name:    FROM_NAME,
      replyTo: email          // hitting Reply goes to the inquirer, not to the script
    });

    return respond({ ok: true });

  } catch (err) {
    return respond({ ok: false, error: String(err) });
  }
}

/**
 * Apps Script serves GET requests to this URL too. Returning something harmless
 * makes it easy to confirm a deployment is live from a browser.
 */
function doGet() {
  return respond({ ok: true, status: 'Inquiry endpoint is deployed.' });
}

function respond(obj) {
  return ContentService
    .createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}

/**
 * Run this once from the Apps Script editor to confirm the script may send mail
 * and that the address is correct. It sends a single test message to TO.
 */
function sendTestEmail() {
  MailApp.sendEmail({
    to:      TO,
    subject: 'Test Site Inquiry — deployment test',
    body:    'If you are reading this, the inquiry endpoint can send mail to this inbox.',
    name:    FROM_NAME
  });
}
