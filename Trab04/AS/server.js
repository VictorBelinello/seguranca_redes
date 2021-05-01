const { validateNewClient } = require('./utils.js');
const crypto = require('crypto');
const express = require('express');
const app = express()
const port = 3000


app.use(express.json())

app.get('/', async (req, res) => {
    const raw = req.body;
    const key = await validateNewClient(raw.ID_C);
    console.log(key);
    if (key !== "") {
        console.log(key);
        const keyBuffer = Buffer.from(key);
        const iv = Buffer.alloc(0);

        const decipher = crypto.createDecipheriv("des-ecb", keyBuffer, iv);

        let decrypted = '';
        decipher.on('readable', () => {
            while (null !== (chunk = decipher.read())) {
                decrypted += chunk.toString('utf8');
            }
        });
        decipher.on('end', () => {
            console.log(decrypted);
            // Prints: some clear text data
        });

        res.send({ "msg": "ok" })
    } else {
        res.send({ "msg": "n ok" })
    }
})

app.listen(port, () => {
    console.log(`Example app listening at http://localhost:${port}`)
})
