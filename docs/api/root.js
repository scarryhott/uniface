'use strict';
const fs = require('fs');
const path = require('path');
const {
  fieldRunSnapshot,
  ingestInternetField,
  paintPublicFaceHtml,
} = require('../closure-field.js');

const HEADERS = {
  'Content-Type': 'text/html; charset=utf-8',
  'Cache-Control': 'no-store',
};

const FACE_HTML = fs.readFileSync(path.join(__dirname, '..', 'index.html'), 'utf8');
const PAN_HTML = fs.readFileSync(path.join(__dirname, '..', 'supernet.html'), 'utf8');

function projectionOf(req) {
  const url = String((req && (req.url || req.originalUrl)) || '/');
  if (/projection=panzoom/i.test(url) || /supernet/i.test(url)) return 'panzoom';
  return 'face';
}

function applyHeaders(res, extra) {
  const headers = extra ? Object.assign({}, HEADERS, extra) : HEADERS;
  Object.keys(headers).forEach(function (key) {
    res.setHeader(key, headers[key]);
  });
}

async function rootBody(req) {
  try {
    await ingestInternetField();
  } catch (err) {}
  const snap = fieldRunSnapshot();
  const projection = projectionOf(req);
  const template = projection === 'panzoom' ? PAN_HTML : FACE_HTML;
  return paintPublicFaceHtml(template, snap);
}

async function handler(req, res) {
  const method = (req && req.method) || 'GET';
  if (method !== 'GET' && method !== 'HEAD') {
    applyHeaders(res, { Allow: 'GET, HEAD' });
    res.statusCode = 405;
    res.end();
    return;
  }
  const body = await rootBody(req);
  applyHeaders(res);
  res.statusCode = 200;
  res.end(method === 'HEAD' ? '' : body);
}

module.exports = handler;
module.exports.rootBody = rootBody;
module.exports.projectionOf = projectionOf;
module.exports.HEADERS = HEADERS;
