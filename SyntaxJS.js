const esprima = require('esprima');
const fs = require('fs');
const path = require('path');
const { Parser } = require('json2csv');

let errorCount = 0;
let functionOrClassCount = 0;
let balancedBracesCount = 0;
let completeFilesCount = 0;
const results = [];
const csvOutputPath = 'syntax_check_results.csv';
const textOutputPath = 'syntax_check_summary.txt';

function hasFunctionOrClass(content) {
    let found = false;
    esprima.parseScript(content, { tolerant: true }, node => {
        if (node.type === 'FunctionDeclaration' || node.type === 'ClassDeclaration') {
            found = true;
            return false; // Stop traversal
        }
    });
    return found;
}

function isBracesBalanced(content) {
    let balance = 0;
    for (let char of content) {
        if (char === '{') {
            balance += 1;
        } else if (char === '}') {
            balance -= 1;
        }
        if (balance < 0) {
            return false; // more closing braces than opening
        }
    }
    return balance === 0;
}

function checkSyntax(filePath) {
    let syntaxOK = false, hasFunctionClass = false, bracesBalanced = false;
    try {
        const content = fs.readFileSync(filePath, 'utf8');
        esprima.parseScript(content);
        syntaxOK = true;
        hasFunctionClass = hasFunctionOrClass(content);
        bracesBalanced = isBracesBalanced(content);
    } catch (error) {
        errorCount++;
    }

    if (syntaxOK) {
        if (hasFunctionClass) functionOrClassCount++;
        if (bracesBalanced) balancedBracesCount++;
        if (hasFunctionClass && bracesBalanced) completeFilesCount++;
    }

    results.push({
        "Code Snippet": filePath,
        "Syntax": syntaxOK ? "OK" : "Error",
        "Function/Class": hasFunctionClass ? "Yes" : "No",
        "Braces": bracesBalanced ? "Balanced" : "Unbalanced"
    });
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

// Replace 'path_to_your_js_files' with the path to your JavaScript files
traverseDirectory('../conversations_new');

// Writing CSV
const json2csvParser = new Parser();
const csv = json2csvParser.parse(results);
fs.writeFileSync(csvOutputPath, csv);

// Writing Text Summary
const textOutput = `Total files with syntax errors: ${errorCount}\nTotal files with function or class definitions: ${functionOrClassCount}\nTotal files with balanced braces: ${balancedBracesCount}\nTotal files that seem complete: ${completeFilesCount}\n`;
fs.writeFileSync(textOutputPath, textOutput);

console.log(`Detailed results written to ${csvOutputPath}`);
console.log(`Summary written to ${textOutputPath}`);
