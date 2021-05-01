const fs = require('fs').promises;


async function validateNewClient(id) {
    const data = await fs.readFile("users.json");
    const users = JSON.parse(data);
    for (let index = 0; index < users.length; index++) {
        const user = users[index];
        if (user.id === id) {
            return user.key;
        }
    }
    return "";
}


module.exports = {
    validateNewClient
}