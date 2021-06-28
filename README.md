# Dunzo_coffee_machine
This repository contains the code for the System Coding round taken during the Dunzo interview



**Requirement:**
1) Serve N beverages in parallel (at max N)
2) Quantity of ingredients used for beverage can vary. And same ingredient can be used for multiple beverages
3) Serve only if all ingredients are available in required quantity
4) Indicator to show ingredients which are running low
5) Refilling the ingredient which is not full
6) Add functional integration test cases for max coverage


This solution is solved using concurrency. That being said that the solution is run on a single machine else we can follow multiprocessing with concurrency.

**My approach:**
1) Applying lock while taking out Ingredients to avoid discrepancies if coffee machine is withdrawing the same ingredient 
2) Choosing at random which beverage to prepare
3) Checking if all the ingredients are available. If available, then prepare else thrown an Exception


Can also use asyncio tasks in Python but this one is more simple and easy to implement.