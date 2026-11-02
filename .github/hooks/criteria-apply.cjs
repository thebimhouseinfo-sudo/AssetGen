#!/usr/bin/env node
'use strict';
// Apply exactly one staged Criteria proposal after a Copilot-observed Advisor turn
// and a NEW Human chat prompt containing the nonce. Hook state is not identity proof.
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const root = path.resolve(__dirname, '..','..');
const proposal = path.join(root,'harness','criteria-proposal.md');
const target = path.join(root,'docs','CRITERIA.md');
const runtime = 'copilot';
const receipt = path.join(root,'harness','criteria-guard.copilot.json');
const hash = b => crypto.createHash('sha256').update(b).digest('hex');
const fileHash = p => fs.existsSync(p) ? hash(fs.readFileSync(p)) : null;
const state = (()=>{try{const value = JSON.parse(fs.readFileSync(receipt,'utf8'));
  return value && value.runtime === runtime ? value : {};}catch{return {};}})();
const mode = process.argv[2] || 'apply';
if (mode === 'status') {
  if (state.phase === 'ADVISED') {
    process.stdout.write('Advisor consulted. Present advice to Human and request a NEW reply exactly: CONFIRM CRITERIA '+state.nonce+'\n');
  } else if (state.phase === 'AUTHORIZED') process.stdout.write('Post-advice chat confirmation received; apply the unchanged staged proposal.\n');
  else process.stdout.write('No valid Advisor consultation. Show draft/delta in chat, await Human request to write, stage proposal, invoke technical-advisor as a subagent.\n');
  process.exit(0);
}
if (mode !== 'apply' || state.phase !== 'AUTHORIZED' || !(Date.now() < state.expiresAt) ||
    state.proposalSha !== fileHash(proposal) || state.baseSha !== fileHash(target)) {
  process.stderr.write('BLOCK: no valid post-advice confirmation for this exact proposed Criteria and existing file.\n');
  process.exit(2);
}
const dest = path.dirname(target);
fs.mkdirSync(dest,{recursive:true});
const temp = target + '.bootstrap.new';
if (fs.existsSync(temp)) {process.stderr.write('BLOCK: pending Criteria transaction; reconcile manually.\n'); process.exit(2);}
try {
  fs.writeFileSync(temp, fs.readFileSync(proposal), {flag:'wx'});
  if (state.baseSha !== fileHash(target)) throw Error('Criteria changed during staging');
  fs.renameSync(temp, target);
  fs.unlinkSync(receipt);
  fs.unlinkSync(proposal);
  process.stdout.write('CRITERIA_APPLIED: exact post-advice proposal saved; one-time confirmation consumed.\n');
} catch(e) {
  if (fs.existsSync(temp)) fs.unlinkSync(temp);
  process.stderr.write('BLOCK: '+e.message+'\n'); process.exit(2);
}
