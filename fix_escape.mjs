import { readFileSync, writeFileSync } from 'fs';

const srcPrompt = 'E:/github有意思的项目/越狱/提示词/claudeopus4.6越狱提示词.md';
const destFile = 'C:/Users/12860/Desktop/cyjcode/src/constants/system.ts';

let prompt = readFileSync(srcPrompt, 'utf8');
// Escape backticks for template literal
prompt = prompt.replace(/`/g, '\`');

const header = `// Critical system constants extracted to break circular dependencies

import { getFeatureValue_CACHED_MAY_BE_STALE } from '../services/analytics/growthbook.js'
import { logForDebugging } from '../utils/debug.js'
import { isEnvDefinedFalsy } from '../utils/envUtils.js'
import { getAPIProvider } from '../utils/model/providers.js'
import { getWorkload } from '../utils/workloadContext.js'

const DEFAULT_PREFIX = \`
`;

const footer = `
\`

const AGENT_SDK_CLAUDE_CODE_PRESET_PREFIX = DEFAULT_PREFIX
const AGENT_SDK_PREFIX = DEFAULT_PREFIX

const CLI_SYSPROMPT_PREFIX_VALUES = [
  DEFAULT_PREFIX,
  AGENT_SDK_CLAUDE_CODE_PRESET_PREFIX,
  AGENT_SDK_PREFIX,
] as const

export type CLISyspromptPrefix = (typeof CLI_SYSPROMPT_PREFIX_VALUES)[number]

export const CLI_SYSPROMPT_PREFIXES: ReadonlySet<string> = new Set(
  CLI_SYSPROMPT_PREFIX_VALUES,
)

export function getCLISyspromptPrefix(options?: {
  isNonInteractive: boolean
  hasAppendSystemPrompt: boolean
}): CLISyspromptPrefix {
  const apiProvider = getAPIProvider()
  if (apiProvider === 'vertex') {
    return DEFAULT_PREFIX
  }

  if (options?.isNonInteractive) {
    if (options.hasAppendSystemPrompt) {
      return AGENT_SDK_CLAUDE_CODE_PRESET_PREFIX
    }
    return AGENT_SDK_PREFIX
  }
  return DEFAULT_PREFIX
}

function isAttributionHeaderEnabled(): boolean {
  if (isEnvDefinedFalsy(process.env.CLAUDE_CODE_ATTRIBUTION_HEADER)) {
    return false
  }
  return getFeatureValue_CACHED_MAY_BE_STALE('tengu_attribution_header', true)
}

export function getAttributionHeader(fingerprint: string): string {
  if (!isAttributionHeaderEnabled()) {
    return ''
  }

  const version = \`\${MACRO.VERSION}.\${fingerprint}\`
  const entrypoint = process.env.CLAUDE_CODE_ENTRYPOINT ?? 'unknown'

  const cch = ' cch=00000;'
  const workload = getWorkload()
  const workloadPair = workload ? \` cc_workload=\${workload};\` : ''
  const header = \`x-anthropic-billing-header: cc_version=\${version}; cc_entrypoint=\${entrypoint};\${cch}\${workloadPair}\`

  logForDebugging(\`attribution header \${header}\`)
  return header
}
`;

const output = header + prompt + footer;
writeFileSync(destFile, output);
console.log('Written ' + output.split('\n').length + ' lines to ' + destFile);
