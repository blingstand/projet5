"""This script use OFF to find a substitute from a given product.

    It uses the module search.py to create a Search object.

    First the user selects a category. Then a product belonging to this category.
    Finally the system finds out an organic substitute of this product.
"""
import  time #os, sys, webbrowser,
from datetime import datetime
import mysql.connector

from modules.interactions import Interactions
from config import Config

class Database(Interactions):
    """ This class uses mysql to get informations """
    TUP_MIF = ("france", "France")
    TUP_BIO_LABELS = ("Bio", "Bio européen", "FR-BIO-01", "AB Agriculture Biologique", \
        "Eco-Emballages", "Organic", "EU Organic")

    def __init__(self):
        config = Config()
        self.mydb = mysql.connector.connect(
            host=config.host,
            user=config.user,
            passwd=config.passwd,
            database=config.database
        )
        self.my_cursor = self.mydb.cursor()

    def _get_prod_from_cat(self, cat):
        """ returns prod from db found with a given category and gathers them in list """

        sql = 'select name from product where category = "{}";'.format(cat)
        self.my_cursor.execute(sql)
        my_result = self.my_cursor.fetchall()
        print(type(my_result))

        list_prod = [prod[0] for prod in my_result]

        return list_prod

    def display_choice_prod(self, my_user, cat):
        """ permits user to make a choice among 20 categories"""

        list_prod = self._get_prod_from_cat(cat)
        answer = None
        while answer is None:
        #loop in order to repeat the input question until an acceptable answer
            self.display_title("Choisir un produit")
            if not my_user.connected:
                print("ATTENTION : vous n'êtes pas connecté, aucune sauvegarde de "\
                    " recherche n'aura lieue !\n")
            ind = self.input_cat_prod("produit", list_prod) #input for cat
            answer = self._check_answer(ind, list_prod, "Un nombre entre 1 et 21 est attendu ! ")

        return answer

    def _get_info_selected_prod(self, name_selected_prod, info):
        """Returns the asked info of a given prod """
        sql = 'select {} from product where name = "{}";'\
            .format(info, name_selected_prod)
        self.my_cursor.execute(sql)
        my_results = self.my_cursor.fetchone() #-> tuple
        if my_results:
            my_results = my_results[0]
            return my_results

    def _after_split_is_in_list(self, name_selected_prod, my_result, my_list):
        """ Returns True or False based on the presence of an element in the given list """
        substitute = None
        try:
            list_result = my_result.split(",")
            for element in list_result:

                if element in my_list:
                    substitute = name_selected_prod
                    return substitute
            return False
        except:
            return False

    def __find_list_low_ns(self, cat, name_selected_prod):
        """ Returns a list of prod with the lowest letter for nbs
            1/ for each prod of my_results checks the nbs
            2/ gets lower => the lower letter of the list
            3/ for each prod of my_results checks wether their nbs == lower
            4/ appends the good ones in list_low_ns
            5/ returns list
        """
        sql = 'select name, nutrition_grade, nb_additives from product where category = "{}";'\
            .format(cat)
        self.my_cursor.execute(sql)
        my_results = self.my_cursor.fetchall()

        ns_selected_prod = self._get_info_selected_prod(name_selected_prod, "nutrition_grade")

        lower_ns = ns_selected_prod
        list_low_ns = [] #stock all the prod with a lower_ns nbs

        for prod in my_results:            #1 -------------
            if prod[1] < lower_ns:
                lower_ns = prod[1]
        # input("ns_selected_prod = {}".format(ns_selected_prod))    #2 -------------

        for prod in my_results:             #3 -------------
            if prod[1] == lower_ns:
                list_low_ns.append(prod)    #4 -------------
        # print("\nVoici la liste des prod à garder :\n", list_lowest)
        return list_low_ns, lower_ns       #5 -------------

    def __compare_additives(self, my_list, lower_ns):
        """ Returns the 1st substitute present in list with the lowest number of additives
            1/ for each prod checks the len(list_additives)
            2/ gets the lower len(list_additives)
            3/ returns the sub with len(list_additives) == lower
        """

        substitute, lower_na = None, 100
        # print("len de my_list :", len(my_list))
        for prod in my_list:
            if prod[2] <= lower_na:
                lower_na = prod[2]
        # print("test lower_na : ", lower_na)
        for prod in my_list:
            if prod[2] == lower_na:
                substitute = prod[0]

        # input("> substitute = {}".format(substitute))
        return substitute, lower_ns, lower_na

    def __test_if_healthier(self, name_selected_prod, lower_ns, lower_na):
        """ Tests if my prod is healthier than sub and returns True or False"""
        nbs = self._get_info_selected_prod(name_selected_prod, "nutrition_grade")
        nba = self._get_info_selected_prod(name_selected_prod, "nb_additives")


        if nbs <= lower_ns and nba <= lower_na:
            return True, name_selected_prod, nbs, nba
        return False, None, None, None

    def _find_healthy_sub(self, cat, name_selected_prod):
        """ Compares our prod with the others in its cat to perhaps return a better
        one for health  """

        list_low_ns, lower_ns = self.__find_list_low_ns(cat, name_selected_prod)
        substitute, lower_ns, lower_na = self.__compare_additives(list_low_ns, lower_ns)
        my_prod_healthier = self.__test_if_healthier(name_selected_prod, lower_ns, lower_na)

        if my_prod_healthier[0]:
            return True, my_prod_healthier[1], my_prod_healthier[2], my_prod_healthier[3]
        return False, substitute, lower_ns, lower_na

    def _get_resp_sub(self, cat, name_selected_prod, info_for_sql, my_list):
        """Return a responsible sub according with info_for_sql"""

        is_str_in_list = self._get_info_selected_prod(name_selected_prod, info_for_sql)
        result_after_split = self._after_split_is_in_list(name_selected_prod, is_str_in_list,\
            my_list)

        if result_after_split:
            return name_selected_prod
        sql = 'select name, {} from product where category = "{}";'.format(info_for_sql, cat)
        self.my_cursor.execute(sql)
        my_results = self.my_cursor.fetchall()
        for prod in my_results:
            if info_for_sql == "palm_oil":
                if prod[1] == "0": # palm_oil == None
                    substitute = prod[0] #prod[0] = name
                    return substitute
                return None
            substitute = self._after_split_is_in_list(prod[0], prod[1], my_list)
            if substitute:
                return substitute
        return None

    def _get_type_resp_sub(self, cat, name_selected_prod):
        """ Returns a substitute that respond to the precised exigence + the precision var """
        title = "Recherche d'un substitut à ce produit {}".format(name_selected_prod)
        self.display_title(title)
        precision = self.get_precision()
        if precision == "1":
            substitute = self._get_resp_sub(cat, name_selected_prod, "palm_oil", [])
        elif precision == "2":
            substitute = self._get_resp_sub(cat, name_selected_prod, \
                "manufacturing_places_tags", self.TUP_MIF)
        elif precision == "3":
            substitute = self._get_resp_sub(cat, name_selected_prod, "labels", \
                self.TUP_BIO_LABELS)
        elif precision == "4":
            return None, "menu"
        else:
            self.negatif_feed_back("Un nombre entre 1 et 4 est attendu")

        return substitute, precision

    def _display_answer(self, cat, name_selected_prod, criterion):
        """ Tries to find a substitute based on criterion

            for health : NutriScore(nbs) and Additives
            for Environnement
        """
        self.display_title("Affichage du substitut")
        #for health
        if criterion == "1": #searches prod from cat
            validate, substitute, lower_ns, lower_na = self._find_healthy_sub(cat, \
                name_selected_prod)
            self.display_title("Affichage de la réponse")
            if validate:
                print("\n", "***"*20, "\n\nJe recommande de garder {}.\n>Il a un nutriscore de {} "\
                "et possède le moins d'additifs ({})\n dans sa catégorie ({}).".\
                format(substitute, lower_ns, lower_na, cat), "\n\n", "***"*20,)
            else:
                print("\n", "***"*20, "\n\nJe recommande ce produit : {}.\n"\
                    "> Il a un nutriscore de {} et possède le moins d'additifs ({})\n "\
                    "dans sa catégorie ({}).".format(substitute, lower_ns, lower_na, cat),\
                    "\n\n", "***"*20,)

        elif criterion == "2":
            substitute, precision = self._get_type_resp_sub(cat, name_selected_prod)
            if precision == "menu":
                return "menu"
            index = int(precision) - 1 #index starts at 0
            criterion = criterion + precision
            self.display_title("Affichage de la réponse")

            if substitute:
                if substitute == name_selected_prod:
                    print("Vous avez demandé un '{}',je vous conseille de garder {}."\
                        .format(self.TUP_PRECISION[index], substitute))
                else:
                    print("Vous avez demandé un '{}', je vous conseille plutôt {}."\
                        .format(self.TUP_PRECISION[index], substitute))
            else:
                substitute = name_selected_prod
                print("Aucun substitut trouvé pour cette catégorie ({}).\n"\
                    "Vous pouvez garder {} dans l'attente de nouveaux produits"\
                    " dans la base\n".format(cat, substitute))
        if criterion in ["0", "1", "21", "22", "23"]:
            return substitute, criterion
        input("il y a un pb =(")

    def get_from_db(self, wanted, name):
        """Checks the db with a select query"""
        sql = 'SELECT {} from product where name = "{}";'.format(wanted, name)
        self.my_cursor.execute(sql)
        my_result = self.my_cursor.fetchone()

        if my_result:
            return my_result[0]
        return None

    def _check_presence_before_insert(self, user_id, substitute_id, product_id, criterion):
        sql = 'SELECT * FROM Search WHERE user_id = {} AND substitute_id = {}'\
        ' AND product_id = {} AND criterion = {};'\
        .format(user_id, substitute_id, product_id, criterion)
        self.my_cursor.execute(sql)
        my_result = self.my_cursor.fetchone()
        if my_result:
            return False
        return True

    def _save_search(self, cat, name_selected_prod, sub, my_user, criterion):
        substitute_id = self.get_from_db("id", sub)
        product_id = self.get_from_db("id", name_selected_prod)
        user_id = my_user.id
        timestamp = datetime.today()
        can_insert = self._check_presence_before_insert(user_id, \
            substitute_id, product_id, criterion)
        if can_insert:
            sql = 'INSERT INTO Search (user_id, substitute_id, day_date, '\
            'product_id, criterion) VALUES ({}, {}, "{}", {}, {});'\
            .format(user_id, substitute_id, timestamp, \
                product_id, criterion)
            self.my_cursor.execute(sql)
            self.mydb.commit()
            print("... recherche enregistrée ...")
        else:
            sql = "UPDATE Search SET day_date = '{}' WHERE product_id = {} AND substitute_id = {} "\
            "AND criterion = {};".format(timestamp, product_id, substitute_id, criterion)
            self.my_cursor.execute(sql)
            self.mydb.commit()
            print("... historique de recherche mise à jour ...")

    def describ_sub(self, sub):
        """Gives to the user the description of a product"""
        components, brands = self.get_from_db("composition", sub), self.get_from_db("brands", sub)
        chain = ""
        if brands is not None:

            chain += " > La marque de ce produit est {}.\n".format(brands)
        if components is not None:
            chain += "-------------- --------------"
            chain += "\n > Voici sa composition : {}.\n".format(components)
            chain += "-------------- --------------"
        if chain != "":
            print(chain)

    def compare_prod_with_sub(self, cat, name_selected_prod, my_user):
        """ Searchs informations about prod and compare them with other prod in the table

        1/  Lets user to choose a criterion : health / environnement
        2/  Returns a substitute according to the criterion if it is possible
        3/  Display a description of the product
        4/  Write the informations concerning the search in the db

        """
        #1
        criterion = "",
        title = "Recherche d'un substitut à ce produit {} ({})".format(name_selected_prod, cat)

        self.display_title(title)

        self.get_criterion()

        #2
        if criterion == "3":
            print("Retour au menu principal ! ")
            time.sleep(1)
            return "menu"

        sub, criterion = self._display_answer(cat, name_selected_prod, criterion)
        if sub == "menu":
            print("Retour au menu principal ! ")
            time.sleep(1)
            return "menu"

        #3
        self.describ_sub(sub)

        #
        if my_user.connected:
            self._save_search(cat, name_selected_prod, sub, my_user, criterion)
        return sub

    def display_more_info_about_product(self, name_selected_prod):
        """ Displays informations about selected prod comming from the db """
        sql = 'SELECT url from Product WHERE name = "{}";'.format(name_selected_prod)
        self.my_cursor.execute(sql)
        my_result = self.my_cursor.fetchone()
        return my_result[0]


# def main():

#     choice = Database()
#     selected_cat = choice.display_choice_cat()
#     name_selected_prod = choice.display_choice_prod(selected_cat)
#     choice.compare_prod_with_sub(selected_cat, name_selected_prod)

#     #******************************************* THE LOOP
#     loop = True
#     while loop:

#         after_search = choice.after_search()
#         if after_search == "1":
#             url = choice.display_more_info_about_product(name_selected_prod)
#             webbrowser.open_new(url)
#             choice.display_title("Ensuite ?")
#         elif after_search == "2":
#             os.system("cls")
#             print("...\nje choisis une autre catégorie : ")
#             selected_cat = choice.display_choice_cat()
#             name_selected_prod = choice.display_choice_prod(selected_cat)
#             choice.compare_prod_with_sub(selected_cat, name_selected_prod)
#         elif after_search == "3":
#             os.system("cls")
#             print("Au revoir :)")
#             sys.exit(0)
# if __name__ == '__main__':
#     main()
