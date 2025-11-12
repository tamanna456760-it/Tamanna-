class JSONAutoFixer {
  constructor() {
    this.fixesApplied = [];
  }
  
  fix(jsonString) {
    this.fixesApplied = [];
    
    try {
      return JSON.parse(jsonString);
    } catch (error) {
      return this.applyFixes(jsonString, error);
    }
  }
  
  applyFixes(jsonString, originalError) {
    let fixed = jsonString;
    
    // Apply fixes in order of severity
    const fixAttempts = [
      this.fixTrailingCommas.bind(this),
      this.fixUnquotedKeys.bind(this),
      this.fixSingleQuotes.bind(this),
      this.fixMissingCommas.bind(this),
      this.fixComments.bind(this),
      this.fixHexNumbers.bind(this),
      this.fixMultilineStrings.bind(this)
    ];
    
    for (const fixAttempt of fixAttempts) {
      try {
        fixed = fixAttempt(fixed);
        const parsed = JSON.parse(fixed);
        return parsed;
      } catch (error) {
        // Continue to next fix attempt
        continue;
      }
    }
    
    throw new Error(`Could not fix JSON: ${originalError.message}`);
  }
  
  fixTrailingCommas(str) {
    const fixed = str
      .replace(/,\s*([}\]])/g, '$1');
    if (fixed !== str) this.fixesApplied.push('Trailing commas removed');
    return fixed;
  }
  
  fixUnquotedKeys(str) {
    const fixed = str
      .replace(/([{,]\s*)([a-zA-Z_$][a-zA-Z0-9_$]*)(\s*:)/g, '$1"$2"$3');
    if (fixed !== str) this.fixesApplied.push('Unquoted keys fixed');
    return fixed;
  }
  
  fixSingleQuotes(str) {
    const fixed = str.replace(/'/g, '"');
    if (fixed !== str) this.fixesApplied.push('Single quotes converted to double quotes');
    return fixed;
  }
  
  fixMissingCommas(str) {
    const fixed = str
      .replace(/"\s*"/g, '","')
      .replace(/([}\]"])\s*([{"])/g, '$1,$2');
    if (fixed !== str) this.fixesApplied.push('Missing commas added');
    return fixed;
  }
  
  fixComments(str) {
    const fixed = str
      .replace(/\/\/.*$/gm, '')
      .replace(/\/\*[\s\S]*?\*\//g, '');
    if (fixed !== str) this.fixesApplied.push('Comments removed');
    return fixed;
  }
  
  fixHexNumbers(str) {
    const fixed = str.replace(/"0x([a-fA-F0-9]+)"/g, (match, hex) => 
      parseInt(hex, 16).toString()
    );
    if (fixed !== str) this.fixesApplied.push('Hex numbers converted');
    return fixed;
  }
  
  fixMultilineStrings(str) {
    const fixed = str.replace(/"[^"]*"/g, match => 
      match.replace(/\n/g, '\\n').replace(/\r/g, '\\r').replace(/\t/g, '\\t')
    );
    if (fixed !== str) this.fixesApplied.push('Multiline strings escaped');
    return fixed;
  }
  
  getFixesApplied() {
    return this.fixesApplied;
  }
}

// Usage
const fixer = new JSONAutoFixer();
const badJSON = `{
  // This is a comment
  name: 'John',
  items: [1, 2, 3,],
  config: {
    debug: true
    version: "1.0"
  }
}`;

try {
  const result = fixer.fix(badJSON);
  console.log('Fixed result:', result);
  console.log('Fixes applied:', fixer.getFixesApplied());
} catch (error) {
  console.error('Failed to fix JSON:', error);
}