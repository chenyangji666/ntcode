import { c as _c } from "react/compiler-runtime";
import * as React from 'react';
import { Box, Text } from '../../ink.js';
import { env } from '../../utils/env.js';

// NTCode - NT Box Logo
// ASCII art NT in box - 9 columns wide, all lines exactly 9 chars

export type ClawdPose = 'default' | 'arms-up' | 'look-left' | 'look-right';

type Props = {
  pose?: ClawdPose;
};

// All lines must be exactly 9 characters (Unicode code points)
const NT_DEFAULT = [
  ' ╭─────╮ ',  // box top
  ' │ N·T │ ',  // NT letters
  ' ╰──┬──╯ ',  // box bottom with stem
  '    │    ',   // stem
  '  ✦ bio  ',  // bioinformatics tag
];

const NT_LOOK_LEFT = [
  '╭─────╮  ',
  '│ N·T │  ',
  '╰──┬──╯  ',
  '   │     ',
  ' ✦ bio   ',
];

const NT_LOOK_RIGHT = [
  '  ╭─────╮',
  '  │ N·T │',
  '  ╰──┬──╯',
  '     │  ',
  '   ✦ bio ',
];

const NT_ARMS_UP = [
  ' ╭─✦─✦─╮ ',  // sparkles on top
  ' │ N·T │ ',
  ' ╰──┬──╯ ',
  '   ╱│╲   ',   // arms up
  '  ✦ bio  ',
];

const POSES: Record<ClawdPose, string[]> = {
  default: NT_DEFAULT,
  'look-left': NT_LOOK_LEFT,
  'look-right': NT_LOOK_RIGHT,
  'arms-up': NT_ARMS_UP,
};

export function Clawd(t0: { pose?: ClawdPose }) {
  const $ = _c(2);
  const pose = t0?.pose ?? 'default';
  const lines = POSES[pose];

  let t1;
  if ($[0] !== lines) {
    t1 = (
      <Box flexDirection="column">
        {lines.map((line, i) => (
          <Text key={i} color="clawd_body">{line}</Text>
        ))}
      </Box>
    );
    $[0] = lines;
    $[1] = t1;
  } else {
    t1 = $[1];
  }
  return t1;
}
