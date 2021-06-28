import json
import random
import threading
import concurrent.futures

class InvalidNumOutletsError(Exception):
    """ An exception thrown when number of outlets are smaller than or equal to 0. """
    def __init__(self, message="Error: Number of outlets should be greater than 0"):
        self.message=message
        super(InvalidNumOutletsError, self).__init__(self.message)


class NoBeverageError(Exception):
    """ An exception thrown when there are no beverages in the system. """
    def __init__(self, message="Error: There are no recipes for beverages in the machine"):
        self.message=message
        super(NoBeverageError, self).__init__(self.message)


class Ingredient:
    """ A class for describing different ingredients available in the coffee machine.

    Parameters
    __________
    name: Name of the inngredient

    available_quantity: Total quantity of this ingredient available in the machine

    _lock: A lock that is acquired everytime the available_quantity is updated by a thread

    """
    def __init__(self, name, value):
        self.name = name
        self.available_quantity = value
        self._lock = threading.Lock()

    
    def getName(self):
        """ Returns the name of the ingredient. """
        return self.name

    
    def getAvailableQuantity(self):
        """ Returns the current available quantity of the ingredient. """
        return self.available_quantity

    
    def getLock(self):
        """ Returns the threading lock associated with this ingredient object. """
        return self._lock

    
    def setAvailableQuantity(self, val):
        """ Sets the available quantity to a new value. """
        self.available_quantity=val


class Beverage:
    """ A class for describing different beverages that the machine can make.

    Parameters
    __________
    name: Name of the beverage

    ingredients: A disctionary of different ingredients and their required quantities

    unavailable_ingredients: List of ingredients that are required but are not available in the machine

    """

    def __init__(self, name, recipe, available_ingredients):
        self.name = name
        self.ingredients={}
        self.unavailable_ingredients=[]

        for item in recipe.keys():
            if item in available_ingredients.keys():
                self.ingredients[available_ingredients[item]]=recipe[item]
            else:
                self.unavailable_ingredients.append(item)

    
    def getName(self):
        """ Return the name of the beverage. """
        return self.name

    
    def getIngredients(self):
        """ Return the ingredients to make the beverage. """
        return self.ingredients

    
    def isAvailable(self):
        """ Returns whether or not all required ingredients are available in the machine. """
        return len(self.unavailable_ingredients)==0

    
    def getUnavailableIngredients(self):
        """ Returns the list of unavailable ingredients. """
        return self.unavailable_ingredients

    
    def getRequiredIngredientQuantity(self, ingredient):
        """ Returns the quantity required for a particular ingredient. """
        return self.ingredients[ingredient]


class Machine:
    """ A class for describing the coffee machine and its functions.

    Parameters
    __________
    num_outlets: Number of outlets in the machine which can work parallely.

    ingredients: A dictionary mapping name of the ingredient to its object.

    beverages: A dictionary mapping name of the beverage to its object.

    print_lock: A threading lock used when printing the output.
                Without this there is some randomness while printing the last character.
                It should be available at the machine level.
    """

    def __init__(self, data):
        
        self.num_outlets = data["machine"]["outlets"]["count_n"]
        
        # Throw an error if number of outlets are smaller than or equal to 0
        if(self.num_outlets<=0):
            raise InvalidNumOutletsError
        
        input_items=data["machine"]["total_items_quantity"]
        self.ingredients = self.getIngredients(input_items)
        self.beverages = self.getBeverages(data["machine"]["beverages"])
        
        # Throw an error if there are no beverages in the system
        if(len(list(self.beverages.keys()))==0):
            raise NoBeverageError
        
        self.print_lock = threading.Lock()
    
    
    def getIngredients(self, input_items):
        """ Takes the json input of ingredients and converts them into objects. 
            Returns the final dictionary mapping name to the object. """
        ingredients={}
        for item in input_items.keys():
            ingredient = Ingredient(item, input_items[item])
            ingredients[item]=ingredient
        return ingredients

    
    def getBeverages(self,beverage_items):
        """ Takes the json input of recipes and converts them into objects.
            Returns the final dictionary mapping name to the recipe. """
        beverages={}
        for item in beverage_items.keys():
            beverage = Beverage(item, beverage_items[item], self.ingredients)
            beverages[item]=beverage
        return beverages

    
    def getIngredientAvailability(self, ingredient_name):
        """ Returns the available quantity of a particular ingredient.
            If not available prints the error. """
        if ingredient_name in self.ingredients.keys():
            return self.ingredients[ingredient_name].getAvailableQuantity()
        print("Ingredient not available in the machine")

    
    def make_beverage(self):
        """ This method works in the following steps:
            1. Chooses a random beverage.
            2. Notifies user if an ingredient is not available for the beverage.
            3. For every ingredient used in the beverage, acquires the lock and updates its value.
            4. Notifies the user if the beverage is made or if an ingredient was insufficient. """

        beverage_item = random.choice(list(self.beverages.items()))
        name, beverage = beverage_item
        required_ingredients = beverage.getIngredients()
        
        if not beverage.isAvailable():
            with self.print_lock:
                print(beverage.getName()+" cannot be prepared because "+", ".join(beverage.getUnavailableIngredients())+" not available")   
            return
        
        made=True # Keeps track of whether the beverage was successfully made
        for ingredient in required_ingredients.keys():
            with ingredient.getLock():
                available_qty = ingredient.getAvailableQuantity()
                required_qty = beverage.getRequiredIngredientQuantity(ingredient)
                
                if available_qty >= required_qty:
                    ingredient.setAvailableQuantity(available_qty-required_qty)
                else:
                    made=False
                    with self.print_lock:
                        print(beverage.getName()+" cannot be prepared as "+ingredient.getName()+" is not sufficiennt")
                    break
        
        if made:
            with self.print_lock:
                print(beverage.getName()+" has been prepared")

    
    def run(self):
        """ This method starts num_outlets number of threads which can make a beverage in parallell. """
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.num_outlets) as executor:
            for index in range(self.num_outlets):
                executor.submit(self.make_beverage)

    
    def refill(self, ingredient_name, new_quantity):
        """ This function refills a particular ingredient to a particular new quantity. """
        if ingredient_name not in self.ingredients.keys():
            print(ingredient_name+" cannot be refilled as it is not available")
            return

        self.ingredients[ingredient_name].setAvailableQuantity(new_quantity)
        print("Updated "+ingredient_name+"'s available quantity to "+str(new_quantity))


if __name__=="__main__":
    f = open("input.txt", "r")    

    try:
        data = json.load(f)
        machine = Machine(data)
    except Exception as e:
        print("Invalid input to the machine. Please check and submit again!")
        print(e)
        exit(0)
    f.close()

    machine.run()   