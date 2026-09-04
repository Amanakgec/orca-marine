const localtunnel = require('localtunnel');
const fs = require('fs');
const path = require('path');

(async () => {
  try {
    const urlFilePath = path.join(__dirname, 'public_url.txt');
    fs.writeFileSync(urlFilePath, 'CONNECTING...\n');

    const tunnel = await localtunnel({ port: 5173 });

    const msg = `URL: ${tunnel.url}\nHOST: 5173\nTIME: ${new Date().toISOString()}\n`;
    fs.writeFileSync(urlFilePath, msg);

    console.log('PUBLIC_URL: ' + tunnel.url);

    tunnel.on('close', () => {
      fs.writeFileSync(urlFilePath, 'CLOSED\n');
      console.log('Tunnel closed.');
      process.exit(0);
    });

    tunnel.on('error', (err) => {
      console.error('Tunnel error:', err);
    });
  } catch (err) {
    console.error('Failed to create localtunnel:', err);
  }
})();
