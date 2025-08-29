import asyncio
import os

from dotenv import load_dotenv
from livekit.api import DeleteIngressRequest, ListIngressRequest, LiveKitAPI

load_dotenv()

API_KEY = os.getenv("LIVEKIT_API_KEY", "")
API_SECRET = os.getenv("LIVEKIT_API_SECRET", "")
SERVER_URL = os.getenv("LIVEKIT_SERVER_URL", "wss://your-project.livekit.cloud")


async def main():
    async with LiveKitAPI(SERVER_URL, API_KEY, API_SECRET) as lk:
        # 列出所有 Ingress
        resp = await lk.ingress.list_ingress(ListIngressRequest())
        for info in resp.items:
            print(info.ingress_id, info.name, info.input_type, info.state.status)

        # 刪掉不需要的（把 ID 換成你要刪的）
        # await lk.ingress.delete_ingress(DeleteIngressRequest(ingress_id="IN_dDZBWYL9FNWZ"))
        # print("deleted:", "<INGRESS_ID_TO_DELETE>")


asyncio.run(main())
