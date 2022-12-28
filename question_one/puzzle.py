import random
import numpy as np
from util import Manhattan


LENGTH=6
WIDTH=6


class Map:
    
    arr=None

    def __init__(self):
        self.arr=np.array([[Cell(a,WIDTH+1-b) for a in range(1,LENGTH+1)]for b in range(1,WIDTH+1)])
        self.ghostUD=self.add_ghost('UD')
        self.ghostLR=self.add_ghost('LR')
        self.exit=self.add_exit()

    def show(self):
        print(self.arr)

    def get_cell(self,x,y):
        return self.arr[WIDTH-y][x-1]

    def add_exit(self,x=LENGTH,y=WIDTH):
        puzzle_exit=Exit()
        self.arr[WIDTH-y][x-1].item=puzzle_exit
        return puzzle_exit

    def add_ghost(self,mode):
        '''添加Ghost，并返回Ghost类'''
        if mode=='UD':
          x,y,forward=4,random.randint(1,6),random.randint(0,1)
          ghost=Ghost(x,y,'UD',forward)
          self.arr[WIDTH-y][x-1].item=ghost
        elif mode=='LR':
          #左右运动的Ghost不选择4作为坐标，防止重复生成
          x,y,forward=random.choice([1,2,3,5,6]),4,random.randint(0,1)
          ghost=Ghost(x,y,'LR',forward)
          self.arr[WIDTH-y][x-1].item=ghost
        else:
          raise Exception("请输入正确的mode")
        return ghost

    def add_robot(self,x=1,y=1):
        '''添加Robot，并返回Robot类'''
        robot = Robot(x,y)
        self.arr[WIDTH-y][x-1].item = robot
        return robot

    def move_ghost(self,mode):
        '''随机移动场景中的Ghost'''
        if mode=='UD':
          if self.ghostUD.forward==0:
            self.arr[WIDTH-self.ghostUD.y][self.ghostUD.x-1].item=None
            if self.ghostUD.y>1:
              self.ghostUD.y -=1
            else:
              self.ghostUD.forward=1
              self.ghostUD.y +=1
            self.arr[WIDTH-self.ghostUD.y][self.ghostUD.x-1].item=self.ghostUD
          elif self.ghostUD.forward==1:
            self.arr[WIDTH-self.ghostUD.y][self.ghostUD.x-1].item=None
            if self.ghostUD.y<LENGTH:
              self.ghostUD.y +=1
            else:
              self.ghostUD.forward=0
              self.ghostUD.y -=1
            self.arr[WIDTH-self.ghostUD.y][self.ghostUD.x-1].item=self.ghostUD
          else:
            raise Exception("错误的前进方向")
        elif mode =='LR':
          if not (isinstance(self.arr[WIDTH-4][4-1].item,Ghost) and
          (self.ghostLR.x,self.ghostLR.y==3,4 or self.ghostLR.x,self.ghostLR.y==5,4)):
            if self.ghostLR.forward==0:
              self.arr[WIDTH-self.ghostLR.y][self.ghostLR.x-1].item=None
              if self.ghostLR.x>1:
                self.ghostLR.x -=1
              else:
                self.ghostLR.forward=1
                self.ghostLR.x +=1
              self.arr[WIDTH-self.ghostLR.y][self.ghostLR.x-1].item=self.ghostLR
            elif self.ghostLR.forward==1:
              self.arr[WIDTH-self.ghostLR.y][self.ghostLR.x-1].item=None
              if self.ghostLR.x<LENGTH:
                self.ghostLR.x +=1
              else:
                self.ghostLR.forward=0
                self.ghostLR.x -=1
              self.arr[WIDTH-self.ghostLR.y][self.ghostLR.x-1].item=self.ghostLR
            else:
              raise Exception("错误的前进方向")
        else:
          raise Exception("错误的模式")

    def set_banner(self,robot):
        '''移除由于墙壁获取不到的单元格'''
        def helper(x1,y1,x2,y2):
          if (robot.x,robot.y)==(x1,y1):
              robot.frontier.remove(self.get_cell(x2,y2))
          if (robot.x,robot.y)==(x2,y2):
              robot.frontier.remove(self.get_cell(x1,y1))
        helper(1,2,1,3)
        helper(2,1,3,1)
        helper(3,2,3,3)
        helper(2,3,2,4)
        helper(3,3,3,4)
        helper(1,5,2,5)
        helper(2,5,2,6)
        helper(3,6,4,6)
        helper(4,2,5,2)
        helper(6,1,6,2)
        helper(4,5,5,5)
        helper(4,4,4,5)
        helper(5,3,5,4)
        helper(4,4,5,4)

class Cell:

    def __init__(self,x,y,item=None,cold=0,dis=20):
        self.x=x
        self.y=y
        self.item=item
        self.cold=cold
        self.dis=dis

    def __repr__(self):  
        if isinstance(self.item,Exit): #Exit
          return '\033[0;32m出\033[0m'
        elif isinstance(self.item,Robot): #Robot
          return '\033[0;34m人\033[0m'
        elif isinstance(self.item,Ghost): #Ghost
          return '\033[0;31m鬼\033[0m'
        else:                           #None
          return '空'

    def __eq__(self,other):
        return self.x==other.x and self.y==other.y and self.item==other.item and self.cold==other.cold
    
    def __hash__(self):
        return hash((self.x,self.y))

    def get_item(self):
        return self.item


class Ghost:

    def __init__(self,x,y,mode,forward):
        '''flag=0，左或者下；flag=1，右或者上'''
        self.x=x
        self.y=y
        self.mode=mode
        self.forward=forward


class Exit:

    def __init__(self,x=LENGTH,y=WIDTH):
        self.x=x
        self.y=y


class Robot:

    def __init__(self,x,y):
        self.x=x
        self.y=y
        #记录走过的方格
        self.trace=[]
        #周围四邻域
        self.frontier=[]

    def feel_cold(self,map,cell):
        '''求单元格在两个幽灵影响下的寒冷值，并返回叠加后的值'''
        dis_toLR=Manhattan(map.ghostLR.x,map.ghostLR.y,cell.x,cell.y)
        dis_toUD=Manhattan(map.ghostUD.x,map.ghostUD.y,cell.x,cell.y)
        def helper(dis):
          if dis==0:
            cold=5
          elif dis==1:
            cold=2
          elif dis==2:
            cold=1
          else:
            cold=0
          return cold
        cold_sum=helper(dis_toLR)+helper(dis_toUD)
        
        return cold_sum

    def get_near(self,map):
        '''得到机器人四邻域，并加入前沿队列'''
        self.frontier.clear()
        x,y=self.x,self.y
        for i in [-1,0,1]:
            for j in [-1,0,1]:
                if x+i <= 0 or x+i >6 or y+j <= 0 or y+j > 6 or i==j or i== -j:
                    continue
                self.frontier.append(map.get_cell(x+i,y+j))
    
    def show_frontier(self):
        '''展示邻域坐标，方便调试'''
        print("邻域为",self.frontier)
        for cell in self.frontier:
            print((cell.x,cell.y),'寒冷为',cell.cold," 曼哈顿距离为",cell.dis)
    
    def show_trace(self):
        '''便于最后展示路线'''
        for cell in self.trace:
            print((cell.x,cell.y),end='->')
    
    def add_trace(self,cell):
        '''将走过的路径加入探索集'''
        if cell not in self.trace:
          self.trace.append(cell)
    
    def evaluate_frontier(self,map):
        '''评估前沿队列，删除其中与探索集的交集，将其按照寒冷值升序'''
        self.get_near(map)
        #map.set_banner(self)
        self.frontier=list(set(self.frontier)-set(self.trace))
        if len(self.frontier)!=0:
          for cell in self.frontier:
              cell.cold=self.feel_cold(map,cell)
          self.frontier.sort(key=lambda x:x.cold)

    def smart_evaluate_frontier(self,map):
        '''评估前沿队列，删除其中与探索集的交集，将其按照寒冷值和启发式函数升序'''
        self.get_near(map)
        map.set_banner(self)
        self.frontier=list(set(self.frontier)-set(self.trace))
        if len(self.frontier)!=0:
          for cell in self.frontier:
              cell.cold=self.feel_cold(map,cell)
              cell.dis=self.feel_dis(map,cell)
          self.frontier.sort(key=lambda x:(x.dis,x.cold,LENGTH-x.x))
    
    def feel_dis(self,map,cell):
        '''返回cell距离出口的曼哈顿距离'''
        dis_to_exit=Manhattan(cell.x,cell.y,map.exit.x,map.exit.y)
        return dis_to_exit
    
    
    def game_over(self,map):
        '''对评估之后的前沿队列做判定，用于判断成功与否'''
        if ((self.x,self.y)==(map.ghostLR.x,map.ghostLR.y))or((self.x,self.y)==(map.ghostUD.x,map.ghostUD.y)): 
            return True
        return False

    def game_win(self,map):
        '''对评估之后的前沿队列做判定，用于判断成功与否'''
        if ((self.x,self.y)==(map.exit.x,map.exit.y)): 
            return True
        return False

    def forsee_safe(self,map):
        '''预知幽灵位置'''
        x1,y1=map.ghostUD.x,map.ghostUD.y
        x2,y2=map.ghostLR.x,map.ghostLR.y
        forward1,forward2=map.ghostUD.forward,map.ghostLR.forward
        if (self.x+1,self.y+1)==(x1,y1) and forward1==0:
            if map.get_cell(self.x+1,self.y) == self.frontier[0]:
                return False
        if (self.x+1,self.y-1)==(x1,y1) and forward1==1:
            if map.get_cell(self.x+1,self.y) == self.frontier[0]:
                return False
        if (self.x+1,self.y-1)==(4,1) and forward1==0:
            if map.get_cell(self.x+1,self.y) == self.frontier[0]:
                return False
        if (self.x+1,self.y+1)==(4,6) and forward1==1:
            if map.get_cell(self.x+1,self.y) == self.frontier[0]:
                return False
        
        
        if (self.x-1,self.y+1)==(x2,y2) and forward2==1:
            if map.get_cell(self.x,self.y+1) == self.frontier[0]:
                return False
        if (self.x+1,self.y+1)==(x2,y2) and forward2==0:
            if map.get_cell(self.x,self.y+1) == self.frontier[0]:
                return False
        if (self.x-1,self.y+1)==(1,4) and forward2==0:
            if map.get_cell(self.x,self.y+1) == self.frontier[0]:
                return False
        return True
    
    
    
    def move(self,map):
        '''读取评估过的前沿队列，选择队列头一个并开始行动'''
        if len(self.frontier)!=0:
            head_cell=self.frontier[0]
            if head_cell.cold <=3:
              current_cell=map.get_cell(self.x,self.y)
              head_cell.item=self
              current_cell.item=None
              self.x,self.y=head_cell.x,head_cell.y
              self.add_trace(head_cell)
            







if __name__ =='__main__':
    pass
    # m=Map()
    # robot=m.add_robot()
    # robot.add_trace(m.get_cell(1,1))

    # m.show()
    
    # print('-----开始运行------')
    # run_level_two(m,robot)
    
    
    
    
    # robot.get_near(m)
    # robot.show_frontier()
    #print(robot.feel_cold(m))
    # print(robot.near)
    # robot.get_near(m)
    # print(robot.near)
    # for i in range(20):
    #     print('-----------------------')
    #     m.show()
    #     robot.get_near(m)
    #     robot.show_frontier()
    #     robot.evaluate_frontier(m)
    #     robot.show_frontier()
    #     if robot.game_over() or robot.game_win(): break
    #     robot.move(m)
        
        
    # m.move_ghost('UD')
    # m.move_ghost('LR')
    #print(robot.feel_cold(m))
    #m.show()

    #print(m.get_cell(4,1).x,m.get_cell(4,1).y)
    # print('--------')
    # m.arr[5][3]='a'
    # m.show()
