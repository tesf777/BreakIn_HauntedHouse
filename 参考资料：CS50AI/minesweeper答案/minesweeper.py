import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # 设置初始长宽和地雷的数目
        self.height = height
        self.width = width
        self.mines = set()

        # 初始化一个无地雷的区域
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # 随机添加地雷
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # 一开始玩家不知道任何地雷At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        '''对元组解耦'''
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        对于一个给定的cell，返回其八邻域内地雷的数量，不包括他自己
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # 循环Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        找到全部雷就胜利
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    关于扫雷的逻辑命题，一个命题包含一个cell集合和这些集合中存在地雷数量
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        返回集合中所有单元格都为地雷的集合
        Returns the set of all cells in self.cells known to be mines.
        """
        if len(self.cells) == self.count:
            return self.cells  
        else:
            return set()

    def known_safes(self):
        """
        返回集合中所有单元格都为安全的集合
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:
            return self.cells
        else:
            return set()

    def mark_mine(self, cell):
        """
        更新知识库里关于一个单元格已知为地雷的知识
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        """
        更新知识库里关于一个单元格已知为安全的知识
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            self.cells.remove(cell)


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # 追踪哪些单元被选过了 Keep track of which cells have been clicked on
        self.moves_made = set()

        # 追踪哪些单元格已知是安全或地雷 Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # 已知正确的命题集合 List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        标记一个单元格为地雷，更新知识库
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)
    
    def conclude(self):
        """
        返回可以从知识库直接推断出的新线索的数量 比如全安全或者全危险
        return the number of new clues that can be directly concluded 
        from the sentences in AI's knowledge base, i.e. the number of 
        cells in one sentence equals count or count == 0
        """
        new_clue = 0
        mine_cells = []
        safe_cells = []
        for sentence in self.knowledge:
            if sentence.known_mines():
                new_clue += 1
                mine_cells += list(sentence.known_mines())
            if sentence.known_safes():
                new_clue += 1
                safe_cells += list(sentence.known_safes())
        if len(mine_cells) > 0:
            for cell in mine_cells:
                self.mark_mine(cell)
        if len(safe_cells) > 0:
            for cell in safe_cells:
                self.mark_safe(cell)
        return new_clue
    
    def infer(self):
        """
        返回可以从知识库推断出的新线索的数量 比如集合1是集合2的子集
        return the number of new clues that can be inferred from 
        AI's knowledge base, i.e. if set1 is a subset of set2, 
        then we can construct the new sentence set2 - set1 = count2 - count1
        """
        new_clue = 0
        new_knowledge = []
        for i in range(len(self.knowledge)):
            for j in range(i + 1, len(self.knowledge)):
                if self.knowledge[i].cells < self.knowledge[j].cells:
                    tmp = Sentence(self.knowledge[j].cells - self.knowledge[i].cells, 
                                   self.knowledge[j].count - self.knowledge[i].count)
                    flag = True
                    for s in self.knowledge:
                        if tmp == s:
                            flag = False
                            break
                    if not flag:
                        continue
                    new_clue += 1
                    new_knowledge.append(tmp)
                elif self.knowledge[j].cells < self.knowledge[i].cells:
                    tmp = Sentence(self.knowledge[i].cells - self.knowledge[j].cells, 
                                   self.knowledge[i].count - self.knowledge[j].count)
                    flag = True
                    for s in self.knowledge:
                        if tmp == s:
                            flag = False
                            break
                    if not flag:
                        continue
                    new_clue += 1
                    new_knowledge.append(tmp)
        self.knowledge += new_knowledge
        return new_clue


    def add_knowledge(self, cell, count):
        """
        当游戏告诉我们时调用，对于一个已知安全的单元格，有多少邻域单元格是地雷
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        self.moves_made.add(cell)
        self.mark_safe(cell)
        x, y = cell
        neighbors = set()
        for i in [-1, 0, 1]:
            for j in [-1, 0, 1]:
                if x+i < 0 or x+i >=self.height or y+j < 0 or y+j >= self.width or (i == j == 0):
                    continue
                neighbors.add((x + i, y + j))
        neighbors = neighbors - self.safes
        neighbor_mines = len(neighbors & self.mines)
        neighbors = neighbors - self.mines
        self.knowledge.append(Sentence(neighbors, count - neighbor_mines))
        while 1:
            new_conclude = self.conclude()
            new_infer = self.infer()       
            if new_conclude == new_infer == 0:
                break

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        safe_moves = self.safes - self.moves_made
        if len(safe_moves) == 0:
            return None
        return list(safe_moves)[0]


    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        possible_moves = set()
        for i in range(self.width):
            for j in range(self.height):
                possible_moves.add((i, j))
        possible_moves -= self.moves_made
        possible_moves -= self.mines
        if len(possible_moves) == 0:
            return None
        return list(possible_moves)[0]
