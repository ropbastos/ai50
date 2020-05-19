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


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """
    p = 1
    for person in people:
        father = people[person]["father"]
        mother = people[person]["mother"]

        # Unconditional probabilities(people with no parental information):
        if father is None and mother is None:
            
            if person in have_trait:
                if person in two_genes:
                    p *= PROBS["gene"][2] * PROBS["trait"][2][True]
                elif person in one_gene:
                    p *= PROBS["gene"][1] * PROBS["trait"][1][True]
                else:
                    p *= PROBS["gene"][0] * PROBS["trait"][0][True]
            else:
                if person in two_genes:
                    p *= PROBS["gene"][2] * PROBS["trait"][2][False]
                elif person in one_gene:
                    p *= PROBS["gene"][1] * PROBS["trait"][1][False]
                else:
                    p *= PROBS["gene"][0] * PROBS["trait"][0][False]
       
        # Conditional probabilities(person has parental information):
        else:
            if person in two_genes:
                if mother in two_genes and father in two_genes:
                    # Probability no gene mutates
                    cond_p = (1 - PROBS["mutation"])**2

                elif ((mother in one_gene and father in two_genes) or 
                        (mother in two_genes and father in one_gene)):
                    # cond_p = (prob. that the fathers/mothers gene doesn't mutate)
                    #  * (prob. that mother/father passes the gene and it doesn't mutate
                    #  or mother/father doesn't pass the gene but what is passed mutatates)
                    cond_p = ( (1 - PROBS["mutation"]) 
                                * ((1 - PROBS["mutation"])*0.5 + PROBS["mutation"]*0.5) )

                elif mother in one_gene and father in one_gene:
                    # Both pass the gene or one doesn't and the other does or both don't.
                    cond_p = ((1 - PROBS["mutation"])*0.5)**2 + (PROBS["mutation"]*(1 - PROBS["mutation"])*0.25)*2 + (PROBS["mutation"]*0.5)**2

                elif ((mother not in one_gene and mother not in two_genes and father in two_genes) or 
                        (mother in two_genes and father not in one_gene and father not in two_genes)):
                        # Probability one gene mutates and the other doesn't.
                        cond_p =  PROBS["mutation"] * (1 - PROBS["mutation"])

                elif ((mother not in one_gene and mother not in two_genes and father in one_gene) or 
                        (mother in one_gene and father not in one_gene and father not in two_genes)):
                        # Probability oone gene mutates and the other either is the gene and doesn't, or isn't and does.
                        cond_p = PROBS["mutation"]*0.5*(1 - PROBS["mutation"]) + 0.5*PROBS["mutation"]**2
                
                elif (mother not in one_gene and mother not in two_genes and father not in one_gene and
                        father not in two_genes):
                        # Probability both mutate.
                        cond_p = PROBS["mutation"]**2
                
                if person in have_trait:
                    cond_p *= PROBS["trait"][2][True]
                else:
                    cond_p *= PROBS["trait"][2][False]
            
            elif person in one_gene:
                if mother in two_genes and father in two_genes:
                    # Probability one gene mutates and the other doesn't.
                    cond_p = PROBS["mutation"] * (1 - PROBS["mutation"]) * 2

                elif ((mother in one_gene and father in two_genes) or 
                        (mother in two_genes and father in one_gene)):
                    # l8r
                    cond_p = (0.5 * (2 * (PROBS["mutation"]*(1-PROBS["mutation"])) + (1-PROBS["mutation"])**2 + PROBS["mutation"]**2) )

                elif mother in one_gene and father in one_gene:
                    # l8r
                    cond_p = (((1-PROBS["mutation"])*0.5)**2 + (PROBS["mutation"]*0.5)**2 + (0.25*(1-PROBS["mutation"])*PROBS["mutation"])*2)*2

                elif ((mother not in one_gene and mother not in two_genes and father in two_genes) or 
                        (mother in two_genes and father not in one_gene and father not in two_genes)):
                        # Probability that neither parent's heredity mutates or both do.
                        cond_p =  (1 - PROBS["mutation"])**2 + PROBS["mutation"]**2

                elif ((mother not in one_gene and mother not in two_genes and father in one_gene) or 
                        (mother in one_gene and father not in one_gene and father not in two_genes)):
                        # l8r
                        cond_p = ( ((PROBS["mutation"])*0.5) * ( (1-PROBS["mutation"]) + PROBS["mutation"] ) 
                                    + 0.5*(1-PROBS["mutation"])**2 + PROBS["mutation"]*(1-PROBS["mutation"])*0.5 )
                
                elif (mother not in one_gene and mother not in two_genes and father not in one_gene and
                        father not in two_genes):
                        # Probability one mutates and the other doesn't.
                        cond_p = PROBS["mutation"] * (1 - PROBS["mutation"]) * 2
                
                if person in have_trait:
                    cond_p *= PROBS["trait"][1][True]
                else:
                    cond_p *= PROBS["trait"][1][False]

            else:
                # Person has no gene.
                if mother in two_genes and father in two_genes:
                    # Probability both genes mutate.
                    cond_p = PROBS["mutation"] * PROBS["mutation"]

                elif ((mother in one_gene and father in two_genes) or 
                        (mother in two_genes and father in one_gene)):
                    # Probability one gene parent passes the gene or doesn't but it mutates
                    # and two genes parent's gene mutates.
                    cond_p = 0.5*PROBS["mutation"]*((1-PROBS["mutation"]) + PROBS["mutation"])
                              
                elif mother in one_gene and father in one_gene:
                    # Probability that both pass the gene or for both it mutates or one mutates the other doesn't.
                    cond_p = ( 0.25 * ( (1-PROBS[ "mutation"])**2 + PROBS["mutation"]**2 + 2*(1-PROBS["mutation"])*PROBS["mutation"] ) )

                elif ((mother not in one_gene and mother not in two_genes and father in two_genes) or 
                        (mother in two_genes and father not in one_gene and father not in two_genes)):
                        # l8r
                        cond_p =  (1 - PROBS["mutation"]) * PROBS["mutation"]

                elif ((mother not in one_gene and mother not in two_genes and father in one_gene) or 
                        (mother in one_gene and father not in one_gene and father not in two_genes)):
                        # l8r
                        cond_p = 0.5*( (1-PROBS["mutation"])**2 + (1-PROBS["mutation"])*PROBS["mutation"] )
                
                elif (mother not in one_gene and mother not in two_genes and father not in one_gene and
                        father not in two_genes):
                        # Probability that none mutates.
                        cond_p = (1 - PROBS["mutation"])**2

                if person in have_trait:
                    cond_p *= PROBS["trait"][0][True]
                else:
                    cond_p *= PROBS["trait"][0][False]

            p *= cond_p

    return p


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    for person in probabilities:
        genes = (
            2 if person in two_genes else
            1 if person in one_gene else
            0
        )

        trait = person in have_trait

        probabilities[person]["gene"][genes] += p
        probabilities[person]["trait"][trait] += p


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    for person in probabilities:
        for field in probabilities[person]:
            total = sum(probabilities[person][field].values())
            for value in probabilities[person][field]:
                probabilities[person][field][value] /= total


if __name__ == "__main__":
    main()
