# pour importer la lib openfoodfact :
# -> pip install git+https://github.com/openfoodfacts/openfoodfacts-python
"""
    Maintenant ma base est remplie par 380 lignes

"""
import sys
from datetime import datetime
import mysql.connector

import openfoodfacts

from config import Config

class FillDb():
    """Tries to fill the db"""
    SIZE_RESEARCH = 50
    SIZE_IN_TAB = 20
    TUP_CATEGORIES = ("Jus de fruits", "Céréales", "Confiture", "Barre chocolatee",\
    "Lait", "Chips", "Bretzels", "Yaourts", "Poissons", "Gâteaux", \
    "Pains de mie", "Charcuterie", "Pizzas", "Tartes salées", "Spaghetti", "Riz",\
    "Glaces", "Chocolat noir", "Soupes", "Compotes")
    TUP_COL = ("product_name", "labels", "additives_original_tags", "packaging",\
        "nutrition_grades", "nova_group", "traces", "manufacturing_places", "minerals_tags",\
        "ingredients_from_or_that_may_be_from_palm_oil_n", "url", "product_quantity", \
        "brands_tags", "nutriments", "ingredients_text")
    TUP_IMP_COL = ("product_name", "additives_original_tags", "nutrition_grades", "labels", \
        "packaging", "manufacturing_places", "ingredients_from_or_that_may_be_from_palm_oil_n",\
        "nova_group", "ingredients_text")
    COLUMNS = 'category, name, labels, additives, nb_additives, packagings, nutrition_grade, '\
    'nova_group, traces, manufacturing_places_tags, minerals_tags, palm_oil, url,'\
    ' quantity, brands, nutriments, composition'

    def __init__(self):

        config = Config()
        self.mydb = mysql.connector.connect(
            host=config.host,
            user=config.user,
            passwd=config.passwd,
            database=config.database
        )
        self.my_cursor = self.mydb.cursor()

    def check_before_fill(self):
        """Checks wether the 400 lines already exists or not"""
        sql = "SELECT COUNT(name) FROM product;"
        self.my_cursor.execute(sql)
        nb_lines = self.my_cursor.fetchone()
        print("Il y a {} lignes écrite(s) dans la base.".format(nb_lines[0]))
        if nb_lines[0] == 0:
            return True
        return False

    def _call_api(self, cat):
        """ Finds 50 prods from a given cat """
        results = openfoodfacts.products.advanced_search({
            "search_terms":"",
            "tagtype_0":"categories ",
            "tag_contains_0":"contains",
            "tag_0": cat,
            "tagtype_1":"countries  ",
            "tag_contains_1":"contains",
            "tag_1":"France",
            "page_size": self.SIZE_RESEARCH})

        list_prod = results["products"] #keeps only the products

        return list_prod

    def _kick_duplicates(self, my_list):
        """ Kickes the prod with a duplicate name"""

        list_prod_name = []
        list_prod = []

        for prod in my_list: #selects prod from list of products
            name = prod["product_name"].lower()
            if name not in list_prod_name: #anti-duplicate name
                list_prod_name.append(name)
                list_prod.append(prod)
        return list_prod

    def _kick_empty_values(self, my_list):
        """kickes a prod from the list if there is no value for 1 selected column"""

        accepted_prod, list_prod = [], []
        kick = 0 #for test
        for prod in my_list:
            for col in self.TUP_IMP_COL:
                try: #to fix error
                    if prod[col] is not None and prod not in accepted_prod:
                        accepted_prod.append(prod)
                except Exception:
                    accepted_prod.remove(prod)
                    kick += 1
                    break
            if prod["product_name"] == "Chocapic Maxi Format": #to fix bug
                accepted_prod.remove(prod)
                kick += 1


        # print("accepted : ",len(accepted_prod), "kicked : ", kick)
        for prod in accepted_prod:
            list_prod.append(prod)

        return list_prod

    def _limit_20(self, my_list):
        """ Limits the number of element at 20 """
        list_20 = []
        for prod in my_list:
            if len(list_20) < 20:
                list_20.append(prod)
        return list_20

    def _keep_selec_col(self, my_list):
        """ return a list filled by dicts of product with only cols present in TUP_COL"""
        new_list = []
        count = 0

        for prod in my_list:
            new_prod = {}
            # print(new_prod, prod["product_name"])
            for key in prod:
                if key in self.TUP_COL:
                    new_prod[key] = prod[key]
            if len(new_prod) == len(self.TUP_COL):
                # print("J'ajoute {} à ma new_liste".format(new_prod["product_name"]))
                new_list.append(new_prod)

        return new_list

    def _get_list_for_cat(self, category):
        """ Searches in API and returns a list of 20 prod """

        first_list_prod = self._call_api(category) #list of 50 prods with same cat

        #list prod with no duplicate names
        list_with_no_duplicate_name = self._kick_duplicates(first_list_prod)

        #list with no empty values for selected columns
        list_without_empty = self._kick_empty_values(list_with_no_duplicate_name)

        #keep just the col writen in self.TUP_COL
        list_prod_with_selec_col = self._keep_selec_col(list_without_empty)

        #list do not pass the SIZE_IN_TAB limit
        list_20_prod = self._limit_20(list_prod_with_selec_col)

        return list_20_prod

    def create_dict_prod(self):
        """Creates the dict_prod with previous functions  """

        dict_prod = {} #create dico

        print(" -- Interroge l'API ! -- ")
        for cat in self.TUP_CATEGORIES: #["Poissons"], list_selected
            list_prod = self._get_list_for_cat(cat)
            #for each cat I fill the dictionnary dict_prod with a list

            dict_prod[cat] = list_prod

        return dict_prod

    def add_substitute(self, category, name, labels, additives, nb_additives, \
        packagings, nutrition_grade, nova_group, traces, manufacturing_places_tags,\
         minerals_tags, palm_oil, url, quantity, brands, nutriments, composition):
        """
        Inserts a line in the table product
        """
        sql = 'INSERT INTO Product ({}) VALUES ("{}", "{}", "{}", "{}", "{}", "{}", '\
        '"{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}");'.format(self.COLUMNS,\
        category, name, labels, additives, nb_additives, packagings, nutrition_grade, nova_group, \
        traces, manufacturing_places_tags, minerals_tags, palm_oil, url, quantity, \
        brands, nutriments, composition)

        self.my_cursor.execute(sql)
        # self.mydb.commit() #has to commit the change
def main():
    before = datetime.now()
    products = FillDb()
    can_fill = products.check_before_fill()
    can_fill = True

    if not can_fill:
        print("Erreur > La base est déjà remplie.")
        sys.exit(0)
    dict_prod = products.create_dict_prod()
    print("Récupération des données terminée")
    progression, ajout = 0, 0
    for key in dict_prod:
        for product in dict_prod[key]:
            category = key
            name = product["product_name"]
            labels = product["labels"]
            additives = product["additives_original_tags"]
            nb_additives = len(product["additives_original_tags"])
            packagings = product["packaging"]
            nutrition_grade = product["nutrition_grades"]
            nova_group = product["nova_group"]
            traces = product["traces"]
            manufacturing_places_tags = product["manufacturing_places"]
            minerals_tags = product["minerals_tags"]
            palm_oil = product["ingredients_from_or_that_may_be_from_palm_oil_n"]
            #page in french
            url = product["url"].replace("https://world.", "https://fr.", 1)
            quantity = int(product["product_quantity"])
            brands = product["brands_tags"]
            nutriments = product["nutriments"] #full of infos
            composition = product["ingredients_text"]

            try:
                if progression == 0:
                    print("Début de l'écriture dans la base")
                    print(" -{}% de l'écriture effectué".format(progression))
                products.add_substitute(category, name, labels, additives, \
                    nb_additives, packagings, nutrition_grade, nova_group, traces,\
                     manufacturing_places_tags, minerals_tags, \
                    palm_oil, url, quantity, brands, nutriments, composition)
                ajout += 1
                progression = progression + ((1/400)*100)
                if progression in [20, 40, 60, 80, 100]:
                    print(" -{}% de l'écriture effectués".format(progression))
            except Exception:
                print("> Il y a un problème pour cette entrée : {}.\n{}".format(name))
                sys.exit(0)

    print("lignes prêtes à être commit : {}/400".format(ajout))
    if ajout == 400:
        products.mydb.commit()
        print("lignes ajoutées à la bases : {}/400".format(ajout))
        after = datetime.now()
        duration = after - before
        print(" -- Temps écoulé pour remplir la base : {} seconds --".format(duration.seconds))
    else:
        raise "Le nombre de lignes ne correspond pas aux attentes du programme."



if __name__ == '__main__':
    main()
