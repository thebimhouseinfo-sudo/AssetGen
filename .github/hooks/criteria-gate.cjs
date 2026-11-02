#!/usr/bin/env node
'use strict';
// Copilot harness hook: procedural Criteria write gate. Not authenticated OS security.
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const root = path.resolve(__dirname, '..', '..');
const target = path.join(root, 'docs', 'CRITERIA.md');
const proposal = path.join(root, 'harness', 'criteria-proposal.md');
const runtime = 'copilot';
const receipt = path.join(root, 'harness', 'criteria-guard.copilot.json');
const sha = data => crypto.createHash('sha256').update(data).digest('hex');
const fileHash = p => fs.existsSync(p) ? sha(fs.readFileSync(p)) : null;
function readState() { try { return JSON.parse(fs.readFileSync(receipt, 'utf8')); } catch { return {}; } }
function save(state) {
  fs.mkdirSync(path.dirname(receipt), {recursive:true});
  const temp = receipt + '.new';
  fs.writeFileSync(temp, JSON.stringify(state, null, 2) + '\n', {mode: 0o600});
  fs.renameSync(temp, receipt);
}
function output(value) { process.stdout.write(JSON.stringify(value) + '\n'); }
function deny(reason) { output({permissionDecision:'deny', permissionDecisionReason: reason}); }
function cleanTool(x) { return String(x || '').toLowerCase(); }
function matchCriteria(s) { return /(?:^|[\\/\s"'=:])(?:docs[\\/])?criteria\.md\b/i.test(s); }
function applyCommand(s) {
  return /^\s*(?:(?:node|node\.exe)\s+)?(?:["']?\.github[\\/]hooks[\\/]criteria-apply\.cjs["']?)(?:\s+apply)?\s*$/i.test(s);
}
function safeReadCommand(s) {
  // Only simple reads with literal arguments. sed can write, rg --pre executes
  // commands, and pagers can launch a shell; a command prefix is not read-only.
  if (/[;&|<>`$\r\n]/.test(s)) return false;
  return /^\s*(?:cat|head|tail|type|Get-Content)\s+(?:[A-Za-z0-9_./\\: -]+|"[A-Za-z0-9_./\\: -]+"|'[A-Za-z0-9_./\\: -]+')\s*$/i.test(s);
}
function toolCommand(args) {
  if (!args || typeof args !== 'object') return '';
  for (const key of ['command', 'cmd', 'script', 'text']) {
    if (typeof args[key] === 'string') return args[key];
  }
  return '';
}
function preTool(event) {
  const name = cleanTool(event.toolName ?? event.tool_name);
  const args = event.toolArgs ?? event.tool_input ?? {};
  const cmd = toolCommand(args);
  const state = readState();
  if (applyCommand(cmd)) {
    if (state.runtime === runtime && state.phase === 'AUTHORIZED' && state.sessionId === (event.sessionId ?? event.session_id) &&
        Date.now() < state.expiresAt && state.proposalSha === fileHash(proposal) &&
        state.baseSha === fileHash(target)) return output({});
    return deny('Criteria is LOCKED. Show a complete draft/delta in chat; Human must ask to write, then consult Technical Advisor, then obtain the Human post-advice confirmation shown by `node .github/hooks/criteria-apply.cjs status`.');
  }
  const mutation = /^(?:edit|create|write|apply_patch|str_replace_editor|bash|powershell|run_in_terminal|execute)$/i.test(name);
  if (!mutation) return output({});
  let serialized = '';
  try { serialized = JSON.stringify(args); } catch { return deny('Unable to inspect tool arguments safely.'); }
  if (!matchCriteria(serialized)) return output({});
  if (['bash','powershell','run_in_terminal','execute'].includes(name) && safeReadCommand(cmd)) return output({});
  return deny('BLOCKED before editing docs/CRITERIA.md. Do NOT call Advisor during brainstorming. First show draft or settled delta in chat, wait for Human request to write, create harness/criteria-proposal.md, invoke technical-advisor as subagent, present advice to Human, await a new Human confirmation and apply only with node .github/hooks/criteria-apply.cjs. Direct Criteria edits are never unlocked.');
}
function advisorStop(event) {
  const agent = cleanTool(event.agentName ?? event.agent_name);
  const sessionId = event.sessionId ?? event.session_id;
  if (agent !== 'technical-advisor' || !sessionId || !fs.existsSync(proposal)) return output({});
  const response = event.response ?? event.last_assistant_message;
  if (typeof response !== 'string' || !response.trim()) return output({});
  const nonce = crypto.randomBytes(4).toString('hex').toUpperCase();
  save({runtime, phase:'ADVISED',sessionId, nonce, proposalSha:fileHash(proposal),
        baseSha:fileHash(target), advisedAt:Date.now()});
  output({});
}
function userPrompt(event) {
  const state = readState();
  const prompt = typeof event.prompt === 'string' ? event.prompt.trim() : '';
  const sessionId = event.sessionId ?? event.session_id;
  if (state.runtime === runtime && state.phase === 'ADVISED' && state.sessionId === sessionId &&
      prompt === 'CONFIRM CRITERIA ' + state.nonce &&
      Date.now() - state.advisedAt < 3600000 &&
      state.proposalSha === fileHash(proposal) && state.baseSha === fileHash(target)) {
    save({...state, phase:'AUTHORIZED', approvedAt:Date.now(), expiresAt:Date.now()+600000});
  }
  output({});
}
function main() {
  const event = JSON.parse(fs.readFileSync(0, 'utf8'));
  if (!event || typeof event !== 'object') throw Error('Expected hook event object');
  const type = process.argv[2] || event.hook_event_name || event.hookEventName ||
    (event.toolName || event.tool_name ? 'preToolUse' : event.agentName ? 'subagentStop' : 'unknown');
  switch(type) {
    case 'sessionStart': case 'SessionStart':
      return output({additionalContext:'Bootstrap Copilot: select Planner. Never write Criteria directly. Advisor is called ONLY after Human asks to finalize a displayed initial draft or settled existing delta, before any Criteria file write. See .github/COPILOT_SETUP.md.'});
    case 'preToolUse': case 'PreToolUse': return preTool(event);
    case 'subagentStop': case 'SubagentStop': return advisorStop(event);
    case 'userPromptSubmitted': case 'UserPromptSubmit': return userPrompt(event);
    default: return output({});
  }
}
try { main(); } catch (err) {
  // preToolUse command errors deny by host, but other events may be nonblocking.
  process.stderr.write('criteria-gate error: ' + err.message + '\n');
  process.exit(2);
}
