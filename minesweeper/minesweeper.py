import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
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
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
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
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
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
        Returns the set of all cells in self.cells known to be mines.
        """
        if self.count != 0 and self.count == len(self.cells):
            return self.cells
        else:
            return None

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0 and len(self.cells) != 0:
            return self.cells
        else:
            return None
        

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1
        

    def mark_safe(self, cell):
        """
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

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
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

    def add_knowledge(self, cell, count):
        """
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
        # Returns list of neighbors to a given cell
        def find_neighbors(cell):
            neighbors = []
            # Row above
            if cell[0]-1 >= 0:
                for abv in range(-1,2):
                    if cell[1]+abv >= 0 and cell[1]+abv < self.width:
                        neighbors.append((cell[0]-1, cell[1]+abv))
            # Row below
            if cell[0]+1 < self.height:
                for blw in range(-1,2):
                    if cell[1]+blw >= 0 and cell[1]+blw < self.width:
                        neighbors.append((cell[0]+1, cell[1]+blw))
            # Side neighbors
            if cell[1]-1 >= 0:
                neighbors.append((cell[0], cell[1]-1))
            if cell[1]+1 < self.width:
                neighbors.append((cell[0], cell[1]+1))
            
            return neighbors

        # Update knowledge in case new inferences can be made.
        def update_kb(new_sentence):
            new_safes = new_sentence.known_safes()
            new_mines = new_sentence.known_mines()

            if new_safes == None and new_mines == None:
                return

            if new_safes:
                self.safes.update(new_safes)
                new_safes_cpy = new_safes.copy()
                for cell in new_safes_cpy:
                    for sentence in self.knowledge:
                        prev_mines = sentence.known_mines()
                        sentence.mark_safe(cell)
                        post_mines = sentence.known_mines()
                        if prev_mines != post_mines:
                            update_kb(sentence)
            else:
                self.mines.update(new_mines)
                new_mines_cpy = new_mines.copy()
                for cell in new_mines_cpy:
                    for sentence in self.knowledge:
                        prev_safes = sentence.known_safes()
                        sentence.mark_mine(cell)
                        post_safes = sentence.known_safes()
                        if prev_safes != post_safes:
                            update_kb(sentence)

        # Subset inferral method
        def subsets(subset_sentence):
            knowledge_cpy = self.knowledge.copy()
            for sentence in knowledge_cpy:
                if sentence.cells.issubset(subset_sentence.cells) and subset_sentence.cells.difference(sentence.cells):
                    resulting_cells = subset_sentence.cells.difference(sentence.cells)
                    resulting_count = subset_sentence.count - sentence.count
                    resulting_sentence = Sentence(resulting_cells, resulting_count)
                    
                    if resulting_sentence.known_safes or resulting_sentence.known_mines:
                        update_kb(resulting_sentence)
                    else:
                        subsets(resulting_sentence)
                        if resulting_sentence not in self.knowledge:
                            self.knowledge.append(resulting_sentence)
                elif subset_sentence.cells.issubset(sentence.cells) and sentence.cells.difference(subset_sentence.cells):
                    resulting_cells = sentence.cells.difference(subset_sentence.cells)
                    resulting_count = sentence.count - subset_sentence.count
                    resulting_sentence = Sentence(resulting_cells, resulting_count)
                    
                    if resulting_sentence.known_safes or resulting_sentence.known_mines:
                        update_kb(resulting_sentence)
                    else:
                        subsets(resulting_sentence)
                        if resulting_sentence not in self.knowledge:
                            self.knowledge.append(resulting_sentence)     
        
        # Mark the cell as a move that's been made.
        self.moves_made.add(cell)

        # Mark the cell as safe and update existing sentences based on that.
        self.mark_safe(cell)

        # Add new sentence to KB.
        neighbors = find_neighbors(cell)

        neighbors_cpy = neighbors.copy()
        for neighbor in neighbors_cpy:
            if neighbor in self.safes:
                neighbors.remove(neighbor)
        
        new_sentence = Sentence(neighbors, count)

        self.knowledge.append(new_sentence)
        
        update_kb(new_sentence) 
        
        # Deals with subsets
        subsets(new_sentence)  

        # Log any new discovered safes
        for sentence in self.knowledge:
            if sentence.known_safes():
                self.safes = self.safes | sentence.known_safes()

        # Cleans up any emptied sentences.
        result = []
        for sentence in self.knowledge:
            if sentence.cells:
                result.append(sentence)
        
        self.knowledge = result
        

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        if self.safes and len(self.safes) > len(self.moves_made):
            while True:
                move = random.choice(tuple(self.safes))
                if move not in self.moves_made:
                    return move
        
        return None


    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        if len(self.mines) != 8:
            while True:
                cell = (random.randrange(self.height), random.randrange(self.width))

                if cell not in self.mines and cell not in self.moves_made:
                    print(f'random move: {cell}')
                    return cell



