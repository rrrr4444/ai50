import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
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
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

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
        for variable in self.crossword.variables:
            for word in self.domains[variable].copy():
                if len(word) != variable.length:
                    self.domains[variable].remove(word)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        changed = False
        location = self.crossword.overlaps[x, y]
        if location:
            i = location[0]
            j = location[1]
            for x_word in self.domains[x].copy():
                match = False
                for y_word in self.domains[y]:
                    if x_word[i] == y_word[j]:
                        match = True
                if match == False:
                    self.domains[x].remove(x_word)
                    changed = True
        return changed

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        queue = list()
        if arcs != None:
            queue = list(arcs)
        else:
            for x in self.crossword.variables:
                for y in self.crossword.variables:
                    if x != y: queue.append((x, y))
        while queue:
            x, y = queue.pop(0)
            if self.revise(x, y):
                if len(self.domains[x]):
                    return False
                neighbors = self.crossword.neighbors(x).remove(y)
                if neighbors: # besides y of course
                    for z in neighbors:
                        queue.append(z, x)


    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        if len(assignment) == len(self.crossword.variables):
            return True
        return False

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        for x in assignment:
            # check if every neighbor overlap is consistent
            for y in self.crossword.neighbors(x):
                if y in assignment:
                    location = self.crossword.overlaps[x, y]
                    if location:
                        i = location[0]
                        j = location[1]
                        if assignment[x][i] != assignment[y][j]:
                            return False
            # check if length of assigned word matches varibale
            if x.length != len(assignment[x]):
                return False
            # make sure all words unique
            for y in assignment:
                if y == x:
                    pass
                elif assignment[x] == assignment[y]:
                    return False
        return True


    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        ordered_domain_values_with_numbers = {value: 0 for value in self.domains[var]}
        unassigned_variables = set()
        for other_var in self.crossword.variables:
            if other_var not in assignment and other_var != var:
                unassigned_variables.add(other_var)
        for word in self.domains[var]:
            for other_var in unassigned_variables:
                location = self.crossword.overlaps[var, other_var]
                i = None
                j = None
                if location:
                    i = location[0]
                    j = location[1]
                    for other_word in self.domains[other_var]:
                        if word[i] != other_word[j]:
                            ordered_domain_values_with_numbers[word] += 1
        ordered_domain_values_with_numbers = sorted(ordered_domain_values_with_numbers.items(), key=lambda x: x[1])
        ordered_domain_values = list()
        for value in ordered_domain_values_with_numbers:
            ordered_domain_values.append(value[0])
        return ordered_domain_values


    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        unassigned_variables = set()
        for variable in self.crossword.variables:
            if variable not in assignment:
                unassigned_variables.add(variable)
        min_domain = [None, None]
        max_domain = [None, None]
        for variable in unassigned_variables:
            if min_domain[1] == None or len(self.domains[variable]) < min_domain[1]:
                min_domain = [variable, len(self.domains[variable])]
            if max_domain[1] == None or len(self.domains[variable]) > max_domain[1]:
                max_domain = [variable, len(self.domains[variable])]
        if min_domain != max_domain:
            return min_domain[0]
        min_degree = [None, None]
        max_degree = [None, None]
        for variable in unassigned_variables:
            degree = len(self.crossword.neighbors(variable))
            if min_degree[1] == None or degree < min_degree[1]:
                min_degree = [variable, degree]
            if max_degree[1] == None or degree > max_degree[1]:
                max_degree = [variable, degree]
        if min_degree != max_degree:
            return max_degree[0]
        return unassigned_variables.pop()


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
        for value in self.order_domain_values(var, assignment):
            assignment[var] = value
            if self.consistent(assignment):
                result = self.backtrack(assignment)
                if result: return result
            assignment.pop(var)
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
