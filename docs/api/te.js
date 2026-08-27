'use strict';
const { ingestInternetField, runSenseSelectTE } = require('../closure-field.js');

const HEADERS = {
  'Content-Type': 'application/json; charset=utf-8',
  'Cache-Control': 'no-store',
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, HEAD, POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type, Accept',
};

const AGENT_SENSE_OF = 'https://chatgpt.com/c/6a8f368d-ae98-83e9-a3e5-7dfc19a9a324';

function applyHeaders(res, extra) {
  const headers = extra ? Object.assign({}, HEADERS, extra) : HEADERS;
  Object.keys(headers).forEach(function (key) {
    res.setHeader(key, headers[key]);
  });
}

function readBody(req) {
  if (req && req.body != null && req.body !== '') {
    if (typeof req.body === 'string') {
      try {
        return Promise.resolve(JSON.parse(req.body));
      } catch (err) {
        return Promise.resolve({ exact: req.body });
      }
    }
    if (typeof req.body === 'object') return Promise.resolve(req.body);
  }
  return new Promise(function (resolve) {
    if (!req || typeof req.on !== 'function') {
      resolve({});
      return;
    }
    const chunks = [];
    req.on('data', function (c) {
      chunks.push(c);
    });
    req.on('end', function () {
      const raw = Buffer.concat(chunks).toString('utf8').trim();
      if (!raw) {
        resolve({});
        return;
      }
      try {
        resolve(JSON.parse(raw));
      } catch (err) {
        resolve({ exact: raw });
      }
    });
    req.on('error', function () {
      resolve({});
    });
  });
}

async function teBody(input) {
  try {
    await ingestInternetField();
  } catch (err) {}
  const sense = Object.assign(
    { of: AGENT_SENSE_OF, kind: 'agent-authored Sense' },
    input && typeof input === 'object' ? input : {}
  );
  if (!sense.of) sense.of = AGENT_SENSE_OF;
  return JSON.stringify(runSenseSelectTE(sense));
}

async function handler(req, res) {
  const method = (req && req.method) || 'GET';
  if (method === 'OPTIONS') {
    applyHeaders(res);
    res.statusCode = 204;
    res.end();
    return;
  }
  if (method !== 'GET' && method !== 'HEAD' && method !== 'POST') {
    applyHeaders(res, { Allow: 'GET, HEAD, POST, OPTIONS' });
    res.statusCode = 405;
    res.end();
    return;
  }
  const input = method === 'POST' ? await readBody(req) : { of: AGENT_SENSE_OF, kind: 'agent-authored Sense' };
  const body = await teBody(input);
  applyHeaders(res);
  res.statusCode = 200;
  res.end(method === 'HEAD' ? '' : body);
}

module.exports = handler;
module.exports.teBody = teBody;
module.exports.HEADERS = HEADERS;
module.exports.AGENT_SENSE_OF = AGENT_SENSE_OF;
