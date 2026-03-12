import { execSync } from 'child_process';
import fs from 'fs';

try {
    execSync('npm run build', { stdio: 'pipe' });
    console.log('Build succeeded');
} catch (error) {
    // Catch stdout and stderr and write to utf8 file
    const errOutput = error.stdout ? error.stdout.toString() : '';
    const errOutput2 = error.stderr ? error.stderr.toString() : '';
    fs.writeFileSync('build_result_utf8.txt', errOutput + '\n' + errOutput2, 'utf8');
    console.log('Build failed. Wrote to build_result_utf8.txt');
}
