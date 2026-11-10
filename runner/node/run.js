'use strict';

// Safe compatibility entrypoint for the currently available Node.js server.
// Legacy AI generation, backup, security simulation, and Git sync modules are
// intentionally not auto-executed during startup.
console.warn('[Tamanna] Legacy full-OS launcher is disabled; starting the available server only.');

require('./server.js');
