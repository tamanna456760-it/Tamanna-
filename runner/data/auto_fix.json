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
