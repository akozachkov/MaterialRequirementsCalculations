import json
from typing import Optional, Tuple

import numpy as np

import process_product_data as ppd

'''
material_requirements_calculations.py
Updated 2025-08-07 14:31
'''
DEFAULT_TARGET_AMOUNT = 100.0


class MaterialRequirementsCalculations:
    """
    Implementation of the linear algorithm to calculate material requirements
    for processes defined on a table of mixes and ingredients.
    
    Based on the algorithm described in:
    "A Linear Algorithm to Calculate Material Requirements for Processes Defined on a Table of Mixes and Ingredients"
    by Alexander L. Kozachkov and Leo A. Kozachkov
    http://kozachkov.com/Alex/linear-algorithm-calculate.pdf
    """
    
    def __init__(self, product_name : str):
        self.product_name = product_name
        self.reader = ppd.ProductTableReaderWriter(product_name, ppd.DEFAULT_PRODUCTS_DIRECTORY, ppd.DEFAULT_CALCULATIONS_DIRECTORY)        
        self.reader.read()

        self.percentage_table = self.reader.percentage_table   
        self.raw_material_names = self.reader.raw_material_names
        self.mix_names = self.reader.mix_names
        self.ingredient_names = self.reader.ingredient_names

        self.raw_material_count = len(self.raw_material_names)
        self.mixes_count = len(self.mix_names)
        self.ingredient_count = len(self.ingredient_names) 
    
    def _calculate_material_requirements(self, target_amount:float=DEFAULT_TARGET_AMOUNT) -> np.ndarray:
        """
        Calculate material requirements using the linear algorithm.
        
        Args:
            percentage_table: The percentage table P where P[i,j] is the percentage 
                            of ingredient i used in mix j
            target_amount: The target amount of the final product
            
        Returns:
            np.ndarray: The target table A where A[i,j] is the amount of ingredient i 
                       used in mix j
        """
      
        n, m = self.percentage_table.shape
        target_table = np.zeros((n, m))
        
        # Step 1: Calculate the last mix (target product)
        # A[i,m] = T * P[i,m] / 100 for i = 1 to n+m-1
        mix_m_total = 0
        for i in range(n):            
            target_table[i, m-1] = target_amount * self.percentage_table[i, m-1] / 100.0
            mix_m_total += target_table[i, m-1]
        
        # Set Target Mix as sum of all it's ingridients. It should equal to target_amount
        if (mix_m_total == target_amount):
            target_table[i, m-1] = mix_m_total
        else:
            raise ValueError("Last mix did not match target_amount: " + str(mix_m_total) + " vs." + str(target_amount))

        print(f"\nStep 1: Last mix (Mix {m}) calculated")
        print(f"Target amount: {target_amount}")
        print(f"Mix {m} amounts: {target_table[:, m-1]}")
        
        # Step 2: Calculate remaining mixes working backwards
        current_table_row_with_mix = n-1
        for j in range(m-2, -1, -1):  # From second-to-last mix to first mix
            # Calculate the amount of mix j needed (Statement 1)
            # T_j = sum of all amounts of mix j used in subsequent mixes
            current_table_row_with_mix -= 1
            mix_j_amount = sum(target_table[current_table_row_with_mix,:]) 
            
            print(f"\nStep {m-j}: Calculating Mix {j+1}")
            print(f"Mix {j+1} amount needed: {mix_j_amount}")
            
            # Calculate amounts for mix j
            # A[i,j] = T_j * P[i,j] / 100 for i = 1 to n+j
            for i in range(min(n+j+1, target_table.shape[0])):
                target_table[i, j] = mix_j_amount * self.percentage_table[i, j] / 100.0

            # Set the amount of mix j itself (it should be equal to the amount needed)
            target_table[current_table_row_with_mix, j] = mix_j_amount   
            
            #print(f"Mix {j+1} amounts: {target_table[:, j]}")
        
        return target_table

    def persist_calculation_request(self, results_string):
        """
        TODO
        Save each request to calculate BOM as csv file
        """

    
    def get_raw_material_totals(self, target_table: np.ndarray) -> np.ndarray:
        """
        Calculate the total amount of each raw material needed.
        
        Args:
            target_table: The target table A
            
        Returns:
            np.ndarray: Array of total amounts for each raw material
        """
        raw_material_totals = np.sum(target_table[:self.raw_material_count, :], axis=1)
        return raw_material_totals  
        
    def _get_results_string(self, percentage_table: np.ndarray, target_table: np.ndarray, 
                        target_amount: float) -> str:
        """
        Generate the results as a formatted string.

        Args:
            percentage_table: The original percentage table
            target_table: The calculated target table
            target_amount: The target amount

        Returns:
            A string containing the formatted results
        """
        lines = []
        lines.append(f"\n{'='*80}")
        lines.append("MATERIAL REQUIREMENTS PLANNING RESULTS")
        lines.append(f"Target Amount: {target_amount}")
        lines.append(f"{'='*80}")

        # Percentage table
        lines.append("\nPERCENTAGE TABLE (Original):")
        lines.append("-" * 65)

        headers = self.mix_names
        row_names = self.ingredient_names

        # Header row
        header_line = f"{'':<15}" + "".join(f"{header:>10}" for header in headers)
        lines.append(header_line)

        # Data rows
        for i, row_name in enumerate(row_names):
            row_line = f"{row_name:<15}"
            for j in range(self.mixes_count):
                if i < self.ingredient_count and j < self.mixes_count:
                    row_line += f"{percentage_table[i, j]:>10.1f}"
                else:
                    row_line += f"{'':>10}"
            lines.append(row_line)

        # Target table
        lines.append("\nTARGET TABLE (Calculated):")
        lines.append("-" * 65)

        # Create a copy of headers + "BOM" without modifying self.mix_names
        headers_with_bom = headers + ["BOM"]

        # Header row
        target_header_line = f"{'':<15}" + "".join(f"{header:>10}" for header in headers_with_bom)
        lines.append(target_header_line)

        # Rows with data + BOM column
        raw_material_totals = self.get_raw_material_totals(target_table)
        for i, row_name in enumerate(row_names):
            row_line = f"{row_name:<15}"
            for j in range(self.mixes_count):
                if i < self.ingredient_count and j < self.mixes_count:
                    row_line += f"{target_table[i, j]:>10.1f}"
                else:
                    row_line += f"{'':>10}"

            if i < len(raw_material_totals):
                row_line += f"{raw_material_totals[i]:>10.1f}"
            else:
                row_line += f"{'n/a':>10}"

            lines.append(row_line)

        # BOM Total
        lines.append(f"\nTotal raw materials needed: {np.sum(raw_material_totals):.1f}")

        # finish output
        lines.append(f"\n{'='*80}")
        lines.append("\n")

        return "\n".join(lines)

    def calculateBOM(self, target_amount: float = DEFAULT_TARGET_AMOUNT):
        """
        Encapsulate entire process
        1. Calculate Target Table
        2. Print everythig for display
        3. Persist the results
        """  

        # Calculate Target Table
        target_table = self._calculate_material_requirements(target_amount) 
       
        # Print everythig for display
        results_string = self._get_results_string(self.percentage_table, target_table, target_amount)
        print(results_string)

        # Persist the results
        self.reader.writeCalculationRequest(results_string)

def main():
    """
    Main function to demonstrate the algorithm with the example from the article.
    """
    product_name = "ActicleExampleProduct"
    mrc = MaterialRequirementsCalculations(product_name)    
    target_amount = 1000.0  
    mrc.calculateBOM(target_amount)

if __name__ == "__main__":
    main() 