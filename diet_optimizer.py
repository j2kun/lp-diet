import csv

from ortools.linear_solver import pywraplp
from ortools.linear_solver.linear_solver_natural_api import SumArray


def from_csv(filename, headers=True):
    '''
        Given the name of a csv file whose first line are headers,
        return a list of dictionaries, one for each row of the file,
        whose keys are the header for that column.
    '''

    with open(filename, 'r') as infile:
        reader = csv.reader(infile)
        lines = [x for x in reader]

    header = lines[0]
    lines = lines[1:]

    table = [dict(zip(header, line)) for line in lines]

    return table


class DietOptimizer(object):
    def __init__(self, nutrient_data_filename='sr28_simple.csv',
                 nutrient_constraints_filename='constraints_simple.csv'):

        self.food_table = from_csv(nutrient_data_filename)

        # clean up food table
        for entry in self.food_table:
            for key in entry:
                if not entry[key].strip():
                    entry[key] = 0.0
                else:
                    try:
                        entry[key] = float(entry[key])
                    except ValueError:
                        pass

        self.constraints_table = from_csv(nutrient_constraints_filename)

        # clean up constraints table
        for entry in self.constraints_table:
            for key in entry:
                try:
                    entry[key] = float(entry[key])
                except ValueError:
                    pass

        self.solver = pywraplp.Solver('diet_optimizer', pywraplp.Solver.GLOP_LINEAR_PROGRAMMING)

        self.create_variable_dict()

        self.special_constraints = {
            'total fat (g)': self.create_fat_constraint,
            'carbohydrate (g)': self.create_carb_constraint,
        }
        self.create_constraints()

        self.objective = self.solver.Objective()
        self.objective.SetMinimization()

    def solve(self):
        '''
            Return a dictionary with 'foods' and 'nutrients' keys representing
            the solution and the nutrient amounts
        '''
        status = self.solver.Solve()
        if status in [self.solver.OPTIMAL, self.solver.FEASIBLE]:
            print('Found feasible solution')
        else:
            raise Exception('Unable to find feasible solution')

        chosen_foods = {
            food_name: var.solution_value()
            for food_name, var in self.variable_dict.items() if var.solution_value() > 1e-10
        }

        self.chosen_foods = chosen_foods

        nutrients = {
            row['nutrient']: self.nutrients_in_diet(chosen_foods, row['nutrient'])
            for row in self.constraints_table
        }

        return {
            'foods': chosen_foods,
            'nutrients': nutrients,
        }

    def nutrients_in_diet(self, chosen_foods, nutrient_name):
        return sum(
            row[nutrient_name] * chosen_foods[row['description']]
            for row in self.food_table if row['description'] in chosen_foods
        )

    def create_variable_dict(self):
        '''
            The variables are the amount of each food to include
        '''
        self.variable_dict = dict(
            (row['description'], self.solver.NumVar(0, self.solver.infinity(), row['description']))
            for row in self.food_table
        )

    def create_constraints(self):
        self.constraint_dict = dict()
        for row in self.constraints_table:
            nutrient = row['nutrient']
            lower_bound = row['lower_bound']
            upper_bound = row['upper_bound']
            self.create_constraint(nutrient, lower_bound, upper_bound)

    def create_constraint(self, nutrient_name, lower, upper):
        '''
            Each constraint is a lower and upper bound on the
            sum of all food variables, scaled by how much of the
            relevant nutrient is in that food.
        '''
        if not lower:
            return

        if nutrient_name in self.special_constraints:
            self.special_constraints[nutrient_name](lower, upper)
            return

        sum_of_foods = self.foods_for_nutrient(nutrient_name)
        constraint_lb = lower <= sum_of_foods
        self.solver.Add(constraint_lb)
        self.constraint_dict[nutrient_name + ' (lower bound)'] = constraint_lb

        if not upper:
            return

        constraint_ub = sum_of_foods <= upper
        self.solver.Add(constraint_ub)
        self.constraint_dict[nutrient_name + ' (upper bound)'] = constraint_ub

    def foods_for_nutrient(self, nutrient_name, scale_by=1.0):
        # a helper function that computes the scaled sum of all food variables
        # for a given nutrient
        relevant_foods = []
        for row in self.food_table:
            var = self.variable_dict[row['description']]
            nutrient_amount = row[nutrient_name]
            if nutrient_amount > 0:
                relevant_foods.append(scale_by * nutrient_amount * var)

        if len(relevant_foods) == 0:
            print('Warning! Nutrient %s has no relevant foods!'.format(nutrient_name))

        '''
            Should be able to use sum, cf. https://github.com/google/or-tools/issues/452
        '''
        return SumArray(relevant_foods)

    def create_fat_constraint(self, lower, upper):
        '''
            Compute the constraint that says the total consumed fat
            must be between 20 and 30 percent of the total calories.
            Despite the name, the value in the data table for fat are as a
            percent of total calories, i.e.

                0.2 * calories <= 9 * fat <= 0.3 * calories
        '''
        fat_name = 'total fat (g)'
        calories_name = 'energy (kcal)'
        calories_lower_bound = self.foods_for_nutrient(calories_name, scale_by=lower/100)
        calories_upper_bound = self.foods_for_nutrient(calories_name, scale_by=upper/100)
        fat = self.foods_for_nutrient(fat_name, scale_by=9.0)

        constraint_lb = calories_lower_bound <= fat
        constraint_ub = fat <= calories_upper_bound
        self.solver.Add(constraint_lb)
        self.solver.Add(constraint_ub)
        self.constraint_dict[fat_name + ' (lower bound)'] = constraint_lb
        self.constraint_dict[fat_name + ' (upper bound)'] = constraint_ub

    def create_carb_constraint(self, lower, upper):
        '''
            Compute the constraint that says the total consumed carbohydrate
            must be between certain percents of the total calories.  Same idea
            as for fat.
        '''
        carbohydrate_name = 'carbohydrate (g)'
        calories_name = 'energy (kcal)'
        calories_lower_bound = self.foods_for_nutrient(calories_name, scale_by=lower/100)
        calories_upper_bound = self.foods_for_nutrient(calories_name, scale_by=upper/100)
        carbohydrate = self.foods_for_nutrient(carbohydrate_name, scale_by=4.0)

        constraint_lb = calories_lower_bound <= carbohydrate
        constraint_ub = carbohydrate <= calories_upper_bound
        self.solver.Add(constraint_lb)
        self.solver.Add(constraint_ub)
        self.constraint_dict[carbohydrate_name + ' (lower bound)'] = constraint_lb
        self.constraint_dict[carbohydrate_name + ' (upper bound)'] = constraint_ub

    def summarize_optimization_problem(self):
        for k, v in self.constraint_dict.items():
            cstr = str(v)
            if len(cstr) > 40:
                print(str(k), '{}...{}'.format(cstr[:20], cstr[-20:]))
            else:
                print(str(k), cstr)

    def summarize_solution(self, solution):
        foods = solution['foods']
        nutrients = solution['nutrients']

        food_rows = {
            row['description']: row for row in self.food_table if row['description'] in foods
        }

        print('Diet:')
        print('-' * 50 + '\n')
        for food in sorted(foods.keys()):
            print('{:4.0f}g: {}'.format(foods[food] * 100, food))
            for nutrient in nutrients:
                if food_rows[food][nutrient] > 0:
                    nutrient_percent = 100 * (food_rows[food][nutrient] * foods[food] / nutrients[nutrient])
                    if nutrient_percent > 0.5:
                        print('\t{:2.0f}% of {}'.format(nutrient_percent, nutrient))
            print()

        print('Nutrient totals')
        print('-' * 50 + '\n')
        for nutrient in nutrients:
            tokens = nutrient.split('(')
            name, unit = '('.join(tokens[:-1]), tokens[-1]
            unit = unit.strip(')')
            print('{:G} {} {}'.format(nutrients[nutrient], unit, name))


if __name__ == "__main__":
    solver = DietOptimizer()
    solution = solver.solve()
    solver.summarize_solution(solution)
