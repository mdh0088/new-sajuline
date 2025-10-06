/* eslint-disable camelcase */

import path from 'node:path';
import sassTrue from 'sass-true/register';

export default {
  spec_dir: 'scss',
  spec_files: ['**/*.{test,spec}.scss'],
  requires: [sassTrue],
  jsLoader: 'import'
}
