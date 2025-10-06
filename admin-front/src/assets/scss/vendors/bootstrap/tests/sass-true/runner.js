'use strict'

import fs from 'node:fs';
import path from 'node:path';
import { runSass } from 'sass-true';

export default (filename, { describe, it }) => {
  const data = fs.readFileSync(filename, 'utf8');
  const TRUE_SETUP = '$true-terminal-output: false; @import "true";';
  const sassString = TRUE_SETUP + data;

  runSass(
      { describe, it, sourceType: 'string' },
      sassString,
      { loadPaths: [path.dirname(filename)] }
  );
}
