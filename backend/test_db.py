import asyncio, motor.motor_asyncio
import certifi

async def test():
    client = motor.motor_asyncio.AsyncIOMotorClient('mongodb+srv://vinaytailor52188_db_user:E6kQ9VBx43s54vMA@bugmindai.woyi2fw.mongodb.net/?appName=BugmindAI&tlsAllowInvalidCertificates=true', tlsCAFile=certifi.where())
    await client.admin.command('ping')
    print('DB Connection Successful')

asyncio.run(test())
