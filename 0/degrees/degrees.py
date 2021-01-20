import csv
import sys
import time


# Map of names to a set of corresponding person_ids
names = {}

# Map of person_ids to a dictionary of: name, birth, movies (a set of movie_ids)
people = {}

# Map of movie_ids to a dictionary of: title, year, stars (a set of person_ids)
movies = {}

# Nodes explored
explored_nodes = []


def load_data(directory):
    """
    Load data from CSV files into memory.
    """
    # Load people
    with open(f"{directory}/people.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            people[row["id"]] = {
                "name": row["name"],
                "birth": row["birth"],
                "movies": set()
            }
            if row["name"].lower() not in names:
                names[row["name"].lower()] = {row["id"]}
            else:
                names[row["name"].lower()].add(row["id"])

    # Load movies
    with open(f"{directory}/movies.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            movies[row["id"]] = {
                "title": row["title"],
                "year": row["year"],
                "stars": set()
            }

    # Load stars
    with open(f"{directory}/stars.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                people[row["person_id"]]["movies"].add(row["movie_id"])
                movies[row["movie_id"]]["stars"].add(row["person_id"])
            except KeyError:
                pass

def main():
    if len(sys.argv) > 2:
        sys.exit("Usage: python degrees.py [directory]")
    directory = sys.argv[1] if len(sys.argv) == 2 else "large"

    # Load data from files into memory
    print("Loading data...")
    load_data(directory)
    print("Data loaded.")

    target = None
    source = None

    while source is None:
        source = person_id_for_name(input("Actor 1: "))
        if source is None:
            print("Person not found.")
    while target is None:
        target = person_id_for_name(input("Actor 2: "))
        if target is None:
            print("Person not found.")

    path = shortest_path(source, target)

    if path is None:
        print("Not connected.")
    else:
        degrees = len(path)
        print(f"{degrees} degrees of separation.")
        path = [(None, source)] + path
        for i in range(degrees):
            person1 = people[path[i][1]]["name"]
            person2 = people[path[i + 1][1]]["name"]
            movie = movies[path[i + 1][0]]["title"]
            print(f"{i + 1}: {person1} and {person2} starred in {movie}")


class Node():
    def __init__(self, movie_id, person_id, parent):
        self.person_id = person_id
        self.movie_id = movie_id
        self.parent = parent


class QueueFrontier():
    def __init__(self):
        self.frontier = []

    def add(self, node):
        self.frontier.append(node)

    def contains_node(self, movie_id, person_id):
        for node in self.frontier:
            if node.movie_id == movie_id:
                if node.person_id == person_id:
                    return True
        return False

    def empty(self):
        return len(self.frontier) == 0

    def remove(self):
        if self.empty():
            raise Exception("empty frontier")
        else:
            node = self.frontier[0]
            self.frontier = self.frontier[1:]
            return node




def in_explored_nodes(movie_id, person_id):
    """
    Returns true if node has already been explored.
    """
    if (movie_id, person_id) in explored_nodes:
        return True
    return False


def generate_path_list(node):
    """
    Finds shortest path between the sorce and the target.
    """

    path_list = []
    while node.parent != None:
        path_list.insert(0,(node.movie_id, node.person_id))
        node = node.parent
    return path_list


def shortest_path(source, target):
    """
    Finds shortest path between the sorce and the target.
    """
    frontier = QueueFrontier()
    source_node = Node(movie_id=None, person_id=source, parent=None)
    frontier.add(source_node)

    while True:
        if frontier.empty() == True:
            return None

        node = frontier.remove()

        if node.person_id == target:

            explored_nodes.append((node.movie_id, node.person_id))
            return generate_path_list(node)
        else:
            explored_nodes.append((node.movie_id, node.person_id))

        for movie_id, person_id in neighbors_for_person(node.person_id):
            if not frontier.contains_node(movie_id, person_id) and not in_explored_nodes(movie_id, person_id):
                child = Node(movie_id=movie_id, person_id=person_id, parent=node)
                if child.person_id == target:
                    return generate_path_list(child)
                frontier.add(child)


def person_id_for_name(name):
    """
    Returns the IMDB id for a person's name,
    resolving ambiguities as needed.
    """
    person_ids = list(names.get(name.lower(), set()))
    if len(person_ids) == 0:
        return None
    elif len(person_ids) > 1:
        print(f"Which '{name}'?")
        for person_id in person_ids:
            person = people[person_id]
            name = person["name"]
            birth = person["birth"]
            print(f"ID: {person_id}, Name: {name}, Birth: {birth}")
        try:
            person_id = input("Intended Person ID: ")
            if person_id in person_ids:
                return person_id
        except ValueError:
            pass
        return None
    else:
        return person_ids[0]


def neighbors_for_person(person_id):
    """
    Returns (movie_id, person_id) pairs for people
    who starred with a given person.
    """
    movie_ids = people[person_id]["movies"]
    neighbors = set()
    for movie_id in movie_ids:
        for person_id in movies[movie_id]["stars"]:
            neighbors.add((movie_id, person_id))
    return neighbors


if __name__ == "__main__":
    main()
