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
function autoFixJSON(jsonString) {
  try {
    // First, try to parse the JSON as-is
    return JSON.parse(jsonString);
  } catch (error) {
    console.log('Attempting to fix malformed JSON...');
    
    // Common JSON fixes
    let fixedJSON = jsonString
      // Fix trailing commas
      .replace(/,\s*}/g, '}')
      .replace(/,\s*]/g, ']')
      // Fix missing quotes around keys
      .replace(/([{,]\s*)([a-zA-Z_$][a-zA-Z0-9_$]*)(\s*:)/g, '$1"$2"$3')
      // Fix single quotes
      .replace(/'/g, '"')
      // Fix missing commas between objects in arrays
      .replace(/}\s*{/g, '},{')
      // Remove comments (single and multi-line)
      .replace(/\/\/.*$/gm, '')
      .replace(/\/\*[\s\S]*?\*\//g, '')
      // Fix unescaped quotes in strings
      .replace(/(?<!\\)"/g, '\\"')
      .replace(/([^\\])"/g, '$1\\"');
    
    try {
      return JSON.parse(fixedJSON);
    } catch (finalError) {
      console.error('Failed to fix JSON:', finalError);
      throw new Error(`Could not fix JSON: ${finalError.message}`);
    }
  }
}

// Usage example
const badJSON = `{
  name: 'John',
  age: 30,
  hobbies: ['reading', 'gaming',],
  "address": {
    street: "123 Main St",
    city: "Boston"
  }
}`;

try {
  const fixed = autoFixJSON(badJSON);
  console.log('Fixed JSON:', fixed);
} catch (error) {
  console.error('Error:', error.message);
}
import React, { useState } from 'react';

const JSONAutoFixEditor = () => {
  const [input, setInput] = useState('');
  const [output, setOutput] = useState('');
  const [error, setError] = useState('');
  const [fixes, setFixes] = useState([]);

  const fixJSON = () => {
    try {
      const fixer = new JSONAutoFixer();
      const result = fixer.fix(input);
      setOutput(JSON.stringify(result, null, 2));
      setFixes(fixer.getFixesApplied());
      setError('');
    } catch (err) {
      setError(err.message);
      setOutput('');
      setFixes([]);
    }
  };

  const validateJSON = () => {
    try {
      JSON.parse(input);
      setError('JSON is valid!');
      setOutput(input);
      setFixes([]);
    } catch (err) {
      setError(`Invalid JSON: ${err.message}`);
    }
  };

  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      <h2>JSON Auto-Fix Tool</h2>
      
      <div style={{ marginBottom: '20px' }}>
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Paste your JSON here..."
          style={{
            width: '100%',
            height: '200px',
            fontFamily: 'monospace',
            fontSize: '14px'
          }}
        />
      </div>
      
      <div style={{ marginBottom: '20px' }}>
        <button onClick={validateJSON} style={{ marginRight: '10px' }}>
          Validate JSON
        </button>
        <button onClick={fixJSON} style={{ marginRight: '10px' }}>
          Auto Fix JSON
        </button>
        <button onClick={() => setInput('')}>
          Clear
        </button>
      </div>
      
      {error && (
        <div style={{
          padding: '10px',
          backgroundColor: error.includes('valid') ? '#d4edda' : '#f8d7da',
          border: `1px solid ${error.includes('valid') ? '#c3e6cb' : '#f5c6cb'}`,
          borderRadius: '4px',
          marginBottom: '20px'
        }}>
          {error}
        </div>
      )}
      
      {fixes.length > 0 && (
        <div style={{ marginBottom: '20px' }}>
          <h4>Fixes Applied:</h4>
          <ul>
            {fixes.map((fix, index) => (
              <li key={index}>{fix}</li>
            ))}
          </ul>
        </div>
      )}
      
      {output && (
        <div>
          <h4>Fixed JSON:</h4>
          <pre style={{
            backgroundColor: '#f8f9fa',
            padding: '15px',
            borderRadius: '4px',
            border: '1px solid #e9ecef',
            overflow: 'auto'
          }}>
            {output}
          </pre>
        </div>
      )}
    </div>
  );
};

export default JSONAutoFixEditor;
