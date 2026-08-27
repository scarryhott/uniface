'use strict';
const { fieldRunSnapshot } = require('../closure-field.js');

const HEADERS = {
  'Content-Type': 'application/json; charset=utf-8',
  'Cache-Control': 'no-store',
};

function fieldRunBody() {
  return JSON.stringify(fieldRunSnapshot());
}

function applyHeaders(res, extra) {
  const headers = extra ? Object.assign({}, HEADERS, extra) : HEADERS;
  Object.keys(headers).forEach(function (key) {
    res.setHeader(key, headers[key]);
  });
}

module.exports = function handler(req, res) {
  const method = (req && req.method) || 'GET';
  if (method !== 'GET' && method !== 'HEAD') {
    applyHeaders(res, { Allow: 'GET, HEAD' });
    res.statusCode = 405;
    res.end();
    return;
  }
  const body = fieldRunBody();
  applyHeaders(res);
  res.statusCode = 200;
  res.end(method === 'HEAD' ? '' : body);
};

module.exports.fieldRunBody = fieldRunBody;
module.exports.HEADERS = HEADERS;
