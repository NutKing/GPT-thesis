const esprima = require('esprima');
const fs = require('fs');
const path = require('path');

const TARGET_DIR = '../conversations_new';
const OUTPUT_DIR = '../Data/snippet_lists_js';

if (!fs.existsSync(OUTPUT_DIR)) {
    fs.mkdirSync(OUTPUT_DIR);
}

const categories = {
    SyntaxError: [],
    HasFunctionOrClass: [],
    BalancedBraces: [],
    Complete: []
};

function hasFunctionOrClass(content) {
    let found = false;
    try {
        esprima.parseScript(content, { tolerant: true }, node => {
            if (node.type === 'FunctionDeclaration' || node.type === 'ClassDeclaration') {
                found = true;
            }
        });
    } catch (err) {
        // Ignore parsing errors here, handled elsewhere
    }
    return found;
}

function isBracesBalanced(content) {
    let balance = 0;
    for (let char of content) {
        if (char === '{') balance++;
        if (char === '}') balance--;
        if (balance < 0) return false;
    }
    return balance === 0;
}

function checkSyntax(filePath) {
    const content = fs.readFileSync(filePath, 'utf8');
    const relPath = path.relative(TARGET_DIR, filePath);

    try {
        esprima.parseScript(content);
        const hasFuncClass = hasFunctionOrClass(content);
        const bracesBalanced = isBracesBalanced(content);

        if (hasFuncClass) categories.HasFunctionOrClass.push(relPath);
        if (bracesBalanced) categories.BalancedBraces.push(relPath);
        if (hasFuncClass && bracesBalanced) categories.Complete.push(relPath);

    } catch (err) {
        categories.SyntaxError.push(relPath);
    }
}

function traverseDirectory(directory) {
    fs.readdirSync(directory).forEach(file => {
        const fullPath = path.join(directory, file);
        if (fs.statSync(fullPath).isDirectory()) {
            traverseDirectory(fullPath);
        } else if (path.extname(fullPath) === '.js') {
            checkSyntax(fullPath);
        }
    });
}

// Start processing
traverseDirectory(TARGET_DIR);

// Write full categorized JSON
fs.writeFileSync(
    path.join(OUTPUT_DIR, 'js_snippet_categories.json'),
    JSON.stringify(categories, null, 4)
);

// Write only Complete snippets to TXT
const completeList = categories.Complete.map(p => `${TARGET_DIR}/${p}`).join('\n');
fs.writeFileSync(path.join(OUTPUT_DIR, 'complete_js_snippets.txt'), completeList);

console.log('\n✅ JavaScript snippet categorization complete. Files saved in', OUTPUT_DIR);
