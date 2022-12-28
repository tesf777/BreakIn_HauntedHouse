from util import Manhattan
from puzzle import Map,Robot,Exit,Cell,Ghost

def run_level_one(m,robot):
    flag=0
    for i in range(30):
        print('---------第%d回合----------'%i)
        m.show()
        robot.get_near(m)
        robot.show_frontier() #初始的前沿队列
        
        robot.evaluate_frontier(m) #最关键的评估函数
        
        robot.show_frontier() #经过排列的前沿队列
        if robot.game_over(m):
            flag=0 
            break
        if robot.game_win(m):
            flag=1
            break
        robot.move(m)
        m.move_ghost('UD')
        m.move_ghost('LR')        
    if flag==1:
      print("本次测试成功，运行回合为：%d,探索集为："%i)
      robot.show_trace()
    else:
      print("本次测试超时或失败，运行回合为：%d,探索集为："%i)
      robot.show_trace()

def run_level_two(m,robot):
    flag=0
    for i in range(30):
        print('---------第%d回合----------'%i)
        m.show()
        #robot.show_frontier() #初始的前沿队列
        
        robot.smart_evaluate_frontier(m) #最关键的评估函数

        robot.show_frontier() #经过排列的前沿队列
        if robot.game_over(m):
            flag=0 
            break
        if robot.game_win(m):
            flag=1
            break
        robot.move(m)
        m.move_ghost('UD')
        m.move_ghost('LR')        
    if flag==1:
      print("本次测试成功，运行回合为：%d,探索集为："%i)
      robot.show_trace()
    else:
      print("本次测试超时或失败，运行回合为：%d,探索集为："%i)
      robot.show_trace() 

if __name__ =='__main__':
    m=Map()
    robot=m.add_robot()
    robot.add_trace(m.get_cell(1,1))

    m.show()
    
    print('-----开始运行------')
    #以寒冷值作为探索标准
    #run_level_one(m,robot)
    #以寒冷值和启发函数(曼哈顿距离)作为探索标准
    #这个level_two效果非常好，和我估计的一样，只是偶尔跑到上面去，导致得到14回合到达终点的结果
    #走的全部都是最短距离，但是会因为有幽灵阻挡，导致静止了几个回合
    run_level_two(m,robot)