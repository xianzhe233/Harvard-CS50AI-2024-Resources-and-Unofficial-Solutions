import sys

from crossword import *
from queue import Queue


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy() for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [[None
                    for _ in range(self.crossword.width)]
                   for _ in range(self.crossword.height)]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new("RGBA", (self.crossword.width * cell_size,
                                 self.crossword.height * cell_size), "black")
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [(j * cell_size + cell_border,
                         i * cell_size + cell_border),
                        ((j + 1) * cell_size - cell_border,
                         (i + 1) * cell_size - cell_border)]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0),
                                                   letters[i][j],
                                                   font=font)
                        draw.text((rect[0][0] + ((interior_size - w) / 2),
                                   rect[0][1] + ((interior_size - h) / 2) - 10),
                                  letters[i][j],
                                  fill="black",
                                  font=font)

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for var in self.domains:
            word_to_remove = []
            for word in self.domains[var]:
                if var.length != len(word):
                    word_to_remove.append(word)

            for word in word_to_remove:
                self.domains[var].remove(word)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revised = False

        if not self.crossword.overlaps[x, y]:
            return False
        else:
            i, j = self.crossword.overlaps[x, y]

        word_to_remove = []
        for x_word in self.domains[x]:
            if any(x_word[i] == y_word[j] for y_word in self.domains[y]):
                continue
            word_to_remove.append(x_word)
            revised = True

        for word in word_to_remove:
            self.domains[x].remove(word)

        return revised

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        # if arcs is None, start with all of the arcs in the problem
        if arcs == None:
            arcs = []
            for var in self.crossword.variables:
                for neighbor in self.crossword.neighbors(var):
                    arcs.append((var, neighbor))

        q = Queue()
        for pair in arcs:
            q.put(pair)

        while not q.empty():
            x, y = q.get()
            if self.revise(x, y):
                if not self.domains[x]:
                    return False
                for z in self.crossword.neighbors(x) - set([y]):
                    q.put((z, x))

        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        for var in self.crossword.variables:
            if var not in assignment:
                return False

        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """

        # distinct check
        if len(assignment.values()) != len(set(assignment.values())):
            return False

        # unary constraint
        for var, word in assignment.items():
            if var.length != len(word):
                return False

        # binary constraint
        for v1, w1 in assignment.items():
            for v2 in self.crossword.neighbors(v1):
                if v2 not in assignment:
                    continue
                w2 = assignment[v2]
                i, j = self.crossword.overlaps[v1, v2]
                if w1[i] != w2[j]:
                    return False

        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """

        def count_elimination(word):
            eliminated_cnt = 0
            for neighbor in self.crossword.neighbors(var):
                if neighbor not in assignment:
                    i, j = self.crossword.overlaps[var, neighbor]
                    for neighbor_word in self.domains[neighbor]:
                        if word[i] != neighbor_word[j]:
                            eliminated_cnt += 1

            return eliminated_cnt

        return sorted(list(self.domains[var]), key=count_elimination)

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """

        def degree(var):
            return len(self.crossword.neighbors(var))

        unassigned = [
            var for var in self.crossword.variables if var not in assignment
        ]

        min_remaining = float('inf')
        best_var = None

        for var in unassigned:
            remaining = len(self.domains[var])

            if remaining < min_remaining:
                min_remaining = remaining
                best_var = var
            elif remaining == min_remaining:
                if degree(var) > degree(best_var):
                    best_var = var

        return best_var

    def inference(self, assignment):
        inferences = {}
        for var in self.crossword.variables:
            if var not in assignment:
                possible_values = []
                for value in self.domains[var]:
                    new_assignment = assignment.copy()
                    new_assignment[var] = value
                    if self.consistent(new_assignment):
                        possible_values.append(value)

                # if there's only one single possible value, add the pair into inferences dict
                if len(possible_values) == 1:
                    inferences[var] = possible_values[0]
        return inferences

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment

        var = self.select_unassigned_variable(assignment)

        for value in self.domains[var]:
            new_assignment = assignment.copy()
            new_assignment[var] = value
            if self.consistent(new_assignment):
                # produce inferences with new assignment value
                inferences = self.inference(new_assignment)
                for inferred_var, inferred_value in inferences.items():
                    new_assignment[inferred_var] = inferred_value

                if self.consistent(new_assignment):
                    result = self.backtrack(new_assignment)
                    if result is not None:
                        return result

        # None for failure
        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
