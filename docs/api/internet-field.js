'use strict';
const { ingestInternetField, internetFieldSnapshot } = require('../closure-field.js');

const HEADERS = {
  'Content-Type': 'application/json; charset=utf-8',
  'Cache-Control': 'no-store',
};

function applyHeaders(res, extra) {
  const headers = extra ? Object.assign({}, HEADERS, extra) : HEADERS;
  Object.keys(headers).forEach(function (key) {
    res.setHeader(key, headers[key]);
  });
}

async function internetFieldBody() {
  await ingestInternetField();
  return JSON.stringify(internetFieldSnapshot());
}

async function handler(req, res) {
  const method = (req && req.method) || 'GET';
  if (method !== 'GET' && method !== 'HEAD') {
    applyHeaders(res, { Allow: 'GET, HEAD' });
    res.statusCode = 405;
    res.end();
    return;
  }
  const body = await internetFieldBody();
  applyHeaders(res);
  res.statusCode = 200;
  res.end(method === 'HEAD' ? '' : body);
}

module.exports = handler;
module.exports.internetFieldBody = internetFieldBody;
module.exports.HEADERS = HEADERS;
