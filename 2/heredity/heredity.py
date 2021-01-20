import csv
import itertools
import sys

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]

def calculate_gene_probability_with_parents(person_name, people, one_gene, two_genes, have_trait):
    # set some constants
    father = people[person_name]["father"]
    mother = people[person_name]["mother"]
    zero_genes = set()
    if father not in one_gene and father not in two_genes:
        zero_genes.add(father)
    if mother not in one_gene and mother not in two_genes:
        zero_genes.add(mother)
    mutation = PROBS["mutation"] # probability of mutation
    # go through all cases and figure out probability of each
    probability = 0
    if person_name in two_genes:
        if father in two_genes and mother in two_genes:
            probability += (1 - mutation) * (1 - mutation)
        elif father in one_gene and mother in one_gene:
            probability += .5 * (1 - mutation) * .5 * (1 - mutation)
            probability += .5 * mutation * .5 * (1 - mutation)
            probability += .5 * (1 - mutation) * .5 * mutation
            probability += .5 * mutation * .5 * mutation
        elif father in zero_genes and mother in zero_genes:
            probability += mutation * mutation
        elif (father in one_gene and mother in two_genes) or (father in two_genes and mother in one_gene):
            probability += .5 * (1 - mutation) * (1 - mutation)
            probability += .5 * mutation * (1 - mutation)
        elif (father in two_genes and mother in zero_genes) or (father in zero_genes and mother in two_genes):
            probability += (1 - mutation) * mutation
        elif (father in one_gene and mother in zero_genes) or (father in zero_genes and mother in one_gene):
            probability += .5 * (1 - mutation) * mutation
            probability += .5 * mutation * mutation
    elif person_name in one_gene:
        if father in two_genes and mother in two_genes:
            probability += (1 - mutation) * mutation
            probability += mutation * (1 - mutation)
        elif father in one_gene and mother in one_gene:
            probability += .5 * mutation * .5 * mutation
            probability += .5 * mutation * .5 * mutation
            probability += .5 * (1 - mutation) * .5 * (1 - mutation)
            probability += .5 * (1 - mutation) * .5 * (1 - mutation)
            probability += .5 * (1 - mutation) * .5 * mutation
            probability += .5 * (1 - mutation) * .5 * mutation
            probability += .5 * (1 - mutation) * .5 * mutation
            probability += .5 * (1 - mutation) * .5 * mutation
        elif father in zero_genes and mother in zero_genes:
            probability += mutation * (1 - mutation)
            probability += (1 - mutation) * mutation
        elif (father in one_gene and mother in two_genes) or (father in two_genes and mother in one_gene):
            probability += .5 * (1 - mutation) * mutation
            probability += .5 * (1 - mutation) * (1 - mutation)
        elif (father in two_genes and mother in zero_genes) or (father in zero_genes and mother in two_genes):
            probability += (1 - mutation) * (1 - mutation)
            probability += mutation * mutation
        elif (father in one_gene and mother in zero_genes) or (father in zero_genes and mother in one_gene):
            probability += .5 * (1 - mutation) * (1 - mutation)
            probability += .5 * (1 - mutation) * mutation
            probability += .5 * mutation * (1 - mutation)
    else:
        if father in two_genes and mother in two_genes:
            probability += mutation * mutation
        elif father in one_gene and mother in one_gene:
            probability += .5 * (1 - mutation) * .5 * (1 - mutation)
            probability += .5 * mutation * .5 * (1 - mutation)
            probability += .5 * (1 - mutation) * .5 * mutation
            probability += .5 * mutation * .5 * mutation
        elif father in zero_genes and mother in zero_genes:
            probability += (1 - mutation) * (1 - mutation)
        elif (father in one_gene and mother in two_genes) or (father in two_genes and mother in one_gene):
            probability += .5 * (1 - mutation) * mutation
            probability += .5 * mutation * mutation
        elif (father in two_genes and mother in zero_genes) or (father in zero_genes and mother in two_genes):
            probability += mutation * (1 - mutation)
        elif (father in one_gene and mother in zero_genes) or (father in zero_genes and mother in one_gene):
            probability += .5 * mutation * (1 - mutation)
            probability += .5 * (1 - mutation) * (1 - mutation)
    return probability


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_genes` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """
    probability = 1

    for person_name in people:
        gene_number = (
        2 if person_name in two_genes else
        1 if person_name in one_gene else
        0
        )
        # probability for gene
        person = people[person_name]
        mother = person["mother"]
        father = person["father"]
        if father == None and mother == None:
            probability *= PROBS["gene"][gene_number]
            probability *= PROBS["trait"][gene_number][person_name in have_trait]
        elif father != None and mother != None:
            probability *= PROBS["trait"][gene_number][person_name in have_trait]
            probability *= calculate_gene_probability_with_parents(person_name, people, one_gene, two_genes, have_trait)

    return probability


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person in `have_gene` and `have_trait`, respectively.
    """
    for person in probabilities:
        if person in one_gene:
            probabilities[person]["gene"][1] += p
        elif person in two_genes:
            probabilities[person]["gene"][2] += p
        else:
            probabilities[person]["gene"][0] += p
        if person in have_trait:
            probabilities[person]["trait"][True] += p
        elif person not in have_trait:
            probabilities[person]["trait"][False] += p


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    for person in probabilities:
        person = probabilities[person]
        gene_prob = person["gene"][0] + person["gene"][1] + person["gene"][2]
        if gene_prob != 0:
            normalizing_value = 1 / gene_prob
            for i in range(3):
                person["gene"][i] *= normalizing_value

        trait_prob = person["trait"][True] + person["trait"][False]
        if trait_prob != 0:
            normalizing_value = 1 / trait_prob
            person["trait"][True] *= normalizing_value
            person["trait"][False] *= normalizing_value

if __name__ == "__main__":
    main()
