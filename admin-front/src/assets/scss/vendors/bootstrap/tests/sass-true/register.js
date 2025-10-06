'use strict'

import path from 'node:path';

const runnerPath = path.join(process.cwd(), 'runner').replace(/\\/g, '/');

require.extensions['.scss'] = (module, filename) => {
  const normalizedFilename = filename.replace(/\\/g, '/')

  return module._compile(`
    const runner = require('${runnerPath}')
    runner('${normalizedFilename}', { describe, it })
    `, filename)
}
