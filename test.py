import machine
import json
import sys
import io
import unittest

class TestCase(unittest.TestCase):

    def test_invalid_json(self):
        """ Tests to check json is valid or not. """
        f = open("test/test_input1.txt", "r")
        with self.assertRaises(Exception):
            data = json.load(f)
        f.close()        

    def test_missing_fields_in_input(self):
        """ Tests if our input contains missing important fields. """
        with self.assertRaises(Exception):
            f = open("test/test_input2.txt", "r")
            data = json.load(f)
            f.close()
            m = machine.Machine(data)
            m.run()         

    def test_0_outlets(self):
        """ Tests if our code would give appropriate error if the number of outlets
            are smaller than or equal to 0. """
        with self.assertRaises(machine.InvalidNumOutletsError):
            f = open("test/test_input3.txt", "r")
            data = json.load(f)
            f.close()
            m = machine.Machine(data)
            m.run()         

    def test_missing_ingredient(self):
        """ Tests that if an ingredient is missing it will say so when the beverage that
            requires it will be made. """
        f = open("test/test_input4.txt", "r")
        data = json.load(f)
        f.close()
        m = machine.Machine(data)
        
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        m.run()
        sys.stdout = sys.__stdout__
        output = capturedOutput.getvalue().strip()
        output=output.split("\n")
        for line in output:
            if "green_tea" in line:
                assert("not available" in line)        

    def test_num_output(self):
        """ Tests that the number of lines of output should be the same as number of outlets. """
        f = open("test/test_input4.txt", "r")
        data = json.load(f)
        f.close()
        num_output = data["machine"]["outlets"]["count_n"]
        m = machine.Machine(data)
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        m.run()
        sys.stdout = sys.__stdout__
        output = capturedOutput.getvalue().strip()
        assert(len(output.split("\n"))==num_output)
        
    def test_no_beverage(self):
        """ Tests that when no beverages are available, an appropriate error is raised. """
        with self.assertRaises(machine.NoBeverageError):
            f = open("test/test_input6.txt", "r")
            data = json.load(f)
            f.close()
            m = machine.Machine(data)
            m.run() 
        
    def test_machine_output(self):
        """ Tests that the value of ingredients is decreased atleast by the amounts used in 
            the beverages that were successfully prepared. """
        f = open("test/test_input4.txt", "r")
        data = json.load(f)
        f.close()
        num_output = data["machine"]["outlets"]["count_n"]
        m = machine.Machine(data)
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        m.run()
        sys.stdout = sys.__stdout__
        output = capturedOutput.getvalue().strip()
        beverages_made = [i.split()[0] for i in output.split("\n") if ("has been prepared" in i)]
        total_ingredients_used={}
        total_ingredients_availabls={}
        for beverage in beverages_made:
            ingredients = data["machine"]["beverages"][beverage]
            for ingredient in ingredients.keys():
                val = ingredients[ingredient]
                if ingredient in total_ingredients_used.keys():
                    total_ingredients_used[ingredient]+=val
                else:
                    total_ingredients_used[ingredient]=val
        for ingredient in total_ingredients_used.keys():
            total_ingredients_availabls[ingredient]=data["machine"]["total_items_quantity"][ingredient]

        for ingredient in total_ingredients_used.keys():
            assert(m.getIngredientAvailability(ingredient)<=total_ingredients_availabls[ingredient]-total_ingredients_used[ingredient])
        
    def test_refill_ingredient(self):
        """ Tests that a particular ingredient is refilled properly or not. """
        f = open("test/test_input4.txt", "r")
        data = json.load(f)
        f.close()
        num_output = data["machine"]["outlets"]["count_n"]
        m = machine.Machine(data)
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        ingredient=list(data["machine"]["total_items_quantity"].keys())[0]
        m.refill(ingredient, 1000)
        sys.stdout = sys.__stdout__
        assert(m.getIngredientAvailability(ingredient)==1000)
        
    def test_no_ingredient(self):
        """ Tests that when no ingredients are available. """
        f = open("test/test_input5.txt", "r")
        data = json.load(f)
        f.close()
        m = machine.Machine(data)
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        m.run()
        sys.stdout = sys.__stdout__
        output = capturedOutput.getvalue().strip()
        for line in output.split("\n"):
            assert("has been prepared" not in line)        

    
if __name__=="__main__":
    unittest.main()
