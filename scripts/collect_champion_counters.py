"""
采集英雄克制关系数据脚本
使用stagehand从op.gg采集英雄克制关系数据
"""
import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from pydantic import BaseModel, Field

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from stagehand import StagehandConfig, Stagehand
from database import engine
from models import ChampionCounter
from services.champion_service import champion_service
from sqlmodel import Session

# 加载环境变量
load_dotenv()


# 定义数据提取模型
class CounterRelation(BaseModel):
    """单个克制关系"""
    name: str = Field(..., description="被克制英雄名称")
    win_rate: str = Field(..., description="胜率百分比,如'53.69'")
    matches: int = Field(..., description="对局场次")


class CounterData(BaseModel):
    """克制关系数据"""
    counters: list[CounterRelation] = Field(..., description="克制关系列表")


# 段位列表
TIERS = ["Emerald", "Diamond", "Master", "Grandmaster", "Challenger"]


async def collect_champion_counters(tier: str = "Emerald"):
    """
    采集指定段位的英雄克制关系数据
    
    Args:
        tier: 段位名称
    """
    # 创建stagehand配置
    config = StagehandConfig(
        env="LOCAL",  # 使用本地浏览器
        model_name="google/gemini-2.5-flash-preview-05-20",
        model_api_key=os.getenv("MODEL_API_KEY"),
        headless=False,  # 显示浏览器窗口以便调试
    )
    
    stagehand = Stagehand(config)
    
    try:
        print(f"\n初始化 Stagehand...")
        await stagehand.init()
        
        page = stagehand.page
        
        # 加载英雄数据
        champion_service.load_champions()
        champions = champion_service.get_all_champions()
        
        print(f"\n开始采集 {tier} 段位的英雄克制关系数据...")
        print(f"共有 {len(champions)} 个英雄需要采集\n")
        
        # 遍历每个英雄
        for idx, (champion_id, champion) in enumerate(champions.items(), 1):
            champion_name = champion.name
            print(f"[{idx}/{len(champions)}] 正在采集 {champion_name} 的克制关系...")
            
            # 访问op.gg英雄克制页面
            url = f"https://op.gg/zh-cn/lol/champions/{champion_id}/counters"
            await page.goto(url)
            
            # 等待页面加载
            await asyncio.sleep(2)
            
            # 提取克制关系数据
            try:
                counter_data = await page.extract(
                    f"提取前10个克制{champion_name}的英雄名称、胜率和场次",
                    schema=CounterData
                )
                
                # 保存到数据库
                with Session(engine) as session:
                    for counter in counter_data.counters:
                        # 根据名称查找被克制英雄的ID
                        counter_champion = champion_service.get_champion_by_name(counter.name)
                        if not counter_champion:
                            print(f"  警告: 未找到英雄 {counter.name}")
                            continue
                        
                        # 解析胜率
                        win_rate = float(counter.win_rate)
                        
                        # 创建克制关系记录
                        champion_counter = ChampionCounter(
                            tier=tier,
                            champion_id=champion_id,
                            champion_name=champion_name,
                            counter_champion_id=counter_champion.id,
                            counter_champion_name=counter.name,
                            win_rate=win_rate,
                            matches=counter.matches
                        )
                        
                        session.add(champion_counter)
                    
                    session.commit()
                    print(f"  成功保存 {len(counter_data.counters)} 条克制关系")
                
            except Exception as e:
                print(f"  错误: {str(e)}")
                continue
            
            # 避免请求过快
            await asyncio.sleep(1)
        
        print(f"\n{tier} 段位数据采集完成!")
        
    finally:
        print("\n关闭 Stagehand...")
        await stagehand.close()


async def main():
    """主函数"""
    # 默认采集Emerald段位
    tier = sys.argv[1] if len(sys.argv) > 1 else "Emerald"
    
    if tier not in TIERS:
        print(f"错误: 无效的段位 '{tier}'")
        print(f"可用段位: {', '.join(TIERS)}")
        return
    
    await collect_champion_counters(tier)


if __name__ == "__main__":
    asyncio.run(main())

