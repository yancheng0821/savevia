const sharp = require('sharp');
const fs = require('fs');
const path = require('path');

const svgPath = path.join(__dirname, 'savevia-web/public/logo.svg');
const pngPath = path.join(__dirname, 'savevia-web/public/logo.png');

sharp(svgPath)
  .png()
  .resize(1200, 1200, {
    fit: 'contain',
    background: { r: 255, g: 255, b: 255, alpha: 0 }
  })
  .toFile(pngPath)
  .then(info => {
    console.log('✓ SVG converted to PNG successfully');
    console.log(`  Output: ${pngPath}`);
    console.log(`  Size: ${info.width}x${info.height}px`);
  })
  .catch(err => {
    console.error('✗ Conversion failed:', err);
    process.exit(1);
  });
