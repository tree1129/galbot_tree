"""
从A点到B点的机器人导航示例
包含重新定位、路径检查和导航功能
"""
from galbot_sdk.g1 import GalbotNavigation, GalbotRobot
import numpy as np
import time

def check_robot_safety():
    """检查机器人安全状态"""
    print("⚠️  注意：1. 请确保机器人急停按钮已释放；2. 请确保机器人周围无障碍物；3. 请确保机器人活动区域清晰")
    while True:
        key = input("请确认机器人急停按钮已释放且周围无障碍物，是否继续？(y/n)...")
        if key == 'y':
            print("用户确认，继续执行...")
            break
        elif key == 'n':
            print("用户取消，退出程序...")
            exit(1)
        else:
            print("输入无效，请输入 'y' 或 'n'")

def navigate_to_point(nav, target_pose, point_name="目标点"):
    """
    导航到指定点位
    
    Parameters:
        nav (GalbotNavigation): 导航实例
        target_pose (list): 目标位姿 [x, y, z, qx, qy, qz, qw]
        point_name (str): 点位名称，用于日志输出
    
    Returns:
        bool: 是否成功到达目标点
    """
    try:
        current_pose = nav.get_current_pose()
        print(f"当前位姿: {current_pose}")
        print(f"开始导航到{point_name}: {target_pose}")
        
        # 检查路径可达性
        if nav.check_path_reachability(target_pose, current_pose):
            print(f"路径可达，开始导航到{point_name}")
            
            retry_count = 3
            while retry_count > 0:
                # 执行导航
                status = nav.navigate_to_goal(
                    target_pose, 
                    enable_collision_check=True, 
                    is_blocking=True, 
                    timeout=30
                )
                
                time.sleep(0.5)
                
                # 检查是否到达目标
                if nav.check_goal_arrival():
                    print(f"✅ 成功到达{point_name}")
                    final_pose = nav.get_current_pose()
                    print(f"最终位姿: {final_pose}")
                    return True
                else:
                    retry_count -= 1
                    print(f"导航失败，剩余重试次数: {retry_count}")
                    print(f"导航状态: {status}")
                    
        else:
            print(f"❌ 路径不可达或不安全，无法到达{point_name}")
            return False
            
    except Exception as e:
        print(f"导航过程中发生异常: {e}")
        return False

def main():
    """主函数：从A点导航到B点"""
    # 安全检查
    check_robot_safety()
    
    # 初始化机器人和导航
    robot = GalbotRobot.get_instance()
    nav = GalbotNavigation.get_instance()
    
    try:
        # 初始化
        if robot.init():
            print("✅ 机器人初始化成功")
        else:
            print("❌ 机器人初始化失败")
            return
            
        if nav.init():
            print("✅ 导航系统初始化成功")
        else:
            print("❌ 导航系统初始化失败")
            return
        
        # 等待数据准备
        time.sleep(1)
        
        # 重新定位逻辑
        init_pose = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0])
        print("开始重新定位...")
        
        while not nav.is_localized():
            nav.relocalize(init_pose)
            time.sleep(0.5)
            print("正在重新定位...")
        
        print("✅ 定位成功")
        current_pose = nav.get_current_pose()
        print(f"当前位姿: {current_pose}")
        
        # 定义起点A和终点B的坐标
        # 根据您提供的实际坐标设置
        point_A = [0.11039125174283981, 0.1474328637123108, 0.0, 0.0, 0.0, -0.05085141962261696, 0.9986996065363742]
        point_B = [1.021070122718811, 1.4370532035827637, 0.0, 0.0, 0.0, 0.7269331042082078, 0.6867062355963478]
        
        print(f"起点A坐标: {point_A}")
        print(f"终点B坐标: {point_B}")
        
        # 循环在A点和B点之间来回移动
        print("\n=== 开始A点和B点之间来回导航 ===")
        print("按 Ctrl+C 可以随时停止程序")
        
        cycle_count = 0
        current_target = "A"  # 先去A点
        
        try:
            while True:
                cycle_count += 1
                print(f"\n{'='*50}")
                print(f"第 {cycle_count} 次循环 - 目标: {current_target}点")
                print(f"{'='*50}")
                
                # 根据当前目标选择目标点
                if current_target == "A":
                    target_pose = point_A
                    target_name = "A点"
                    next_target = "B点"
                else:
                    target_pose = point_B
                    target_name = "B点"
                    next_target = "A点"
                
                # 导航到当前目标点
                success = navigate_to_point(nav, target_pose, target_name)
                
                if success:
                    print(f"✅ 成功到达{target_name}，立即前往{next_target}")
                    current_target = "A" if current_target == "B" else "B"
                    # 短暂等待后立即前往下一个点
                    time.sleep(1)
                else:
                    print(f"❌ 未能到达{target_name}，1秒后重试...")
                    time.sleep(1)
                    
        except KeyboardInterrupt:
            print(f"\n\n⏹️  用户中断程序，已完成 {cycle_count} 次循环")
            print("正在安全停止...")
            
        except Exception as e:
            print(f"\n❌ 程序执行过程中发生异常: {e}")
            
        print(f"📊 总共完成了 {cycle_count} 次导航循环")
            
    except Exception as e:
        print(f"程序执行过程中发生异常: {e}")
        
    finally:
        # 停止导航
        nav.stop_navigation()
        print("导航已停止")
        
        # 释放资源
        robot.request_shutdown()
        robot.wait_for_shutdown()
        robot.destroy()
        print("✅ 资源释放成功")

if __name__ == "__main__":
    main()
