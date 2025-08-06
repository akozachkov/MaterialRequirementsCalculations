import numpy as np
from typing import Tuple, Optional
import json
from process_product_data import ProductTableReaderWriter

'''
material_requirements_calculations.py
Updated 2025-08-06 11:33
'''

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
        reader = ProductTableReaderWriter(product_name, "products")
        self.percentage_table, self.ingredient_names, self.mix_names = reader.read()

        self.raw_materials_count = len(self.ingredient_names)
        self.mixes_count = len(self.mix_names)
        self.total_rows = self.raw_materials_count + self.mixes_count
        self.total_cols = self.mixes_count      
    
    def calculate_material_requirements(self, target_amount: float) -> np.ndarray:
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
        for j in range(m-2, -1, -1):  # From second-to-last mix to first mix
            # Calculate the amount of mix j needed (Statement 1)
            # T_j = sum of all amounts of mix j used in subsequent mixes
            mix_j_amount = 0
            #for k in range(j+1, m):
                # Mix j is at row n+j (0-indexed)
                #if n+j < target_table.shape[0]:
                    #mix_j_amount += target_table[n+j, k]

            for k in range(j+1, m-1):
                mix_j_amount += target_table[n+j, k]
            
            print(f"\nStep {m-j}: Calculating Mix {j+1}")
            print(f"Mix {j+1} amount needed: {mix_j_amount}")
            
            # Calculate amounts for mix j
            # A[i,j] = T_j * P[i,j] / 100 for i = 1 to n+j
            for i in range(min(n+j+1, target_table.shape[0])):
                target_table[i, j] = mix_j_amount * self.percentage_table[i, j] / 100.0
            
            # Set the amount of mix j itself (it should be equal to the amount needed)
            if n+j < target_table.shape[0]:
                target_table[n+j, j] = mix_j_amount
            
            print(f"Mix {j+1} amounts: {target_table[:, j]}")
        
        return target_table
    
    def get_raw_material_totals(self, target_table: np.ndarray) -> np.ndarray:
        """
        Calculate the total amount of each raw material needed.
        
        Args:
            target_table: The target table A
            
        Returns:
            np.ndarray: Array of total amounts for each raw material
        """
        raw_material_totals = np.sum(target_table[:self.raw_materials_count, :], axis=1)
        return raw_material_totals
    
    def print_results(self, percentage_table: np.ndarray, target_table: np.ndarray, 
                     target_amount: float):
        """
        Print the results in a formatted way.
        
        Args:
            percentage_table: The original percentage table
            target_table: The calculated target table
            target_amount: The target amount
        """
        print(f"\n{'='*60}")
        print(f"MATERIAL REQUIREMENTS PLANNING RESULTS")
        print(f"Target Amount: {target_amount}")
        print(f"{'='*60}")
        
        # Print percentage table
        print("\nPERCENTAGE TABLE (Original):")
        print("-" * 50)
        headers = [f"Mix {i+1}" for i in range(self.mixes_count)]
        row_names = [f"Raw Material {i+1}" for i in range(self.raw_materials_count)]
        row_names.extend([f"Mix {i+1}" for i in range(self.mixes_count)])
        
        # Print header
        print(f"{'':<15}", end="")
        for header in headers:
            print(f"{header:>10}", end="")
        print()
        
        # Print rows
        for i, row_name in enumerate(row_names):
            print(f"{row_name:<15}", end="")
            for j in range(self.mixes_count):
                if i < self.total_rows and j < self.total_cols:
                    print(f"{percentage_table[i, j]:>10.1f}", end="")
                else:
                    print(f"{'':>10}", end="")
            print()
        
        # Print target table
        print(f"\nTARGET TABLE (Calculated):")
        print("-" * 50)
        
        # Print header
        print(f"{'':<15}", end="")
        for header in headers:
            print(f"{header:>10}", end="")
        print()
        
        # Print rows
        for i, row_name in enumerate(row_names):
            print(f"{row_name:<15}", end="")
            for j in range(self.mixes_count):
                if i < self.total_rows and j < self.total_cols:
                    print(f"{target_table[i, j]:>10.1f}", end="")
                else:
                    print(f"{'':>10}", end="")
            print()
        
        # Print raw material totals
        raw_totals = self.get_raw_material_totals(target_table)
        print(f"\nRAW MATERIAL TOTALS:")
        print("-" * 30)
        for i in range(self.raw_materials_count):
            print(f"Raw Material {i+1}: {raw_totals[i]:.1f}")
        
        print(f"\nTotal raw materials needed: {np.sum(raw_totals):.1f}")
    
    def create_custom_table(self, raw_materials: int, mixes: int) -> np.ndarray:
        """
        Create a custom table with specified dimensions.
        
        Args:
            raw_materials: Number of raw materials
            mixes: Number of mixes
            
        Returns:
            np.ndarray: Empty table with proper dimensions
        """
        n = raw_materials + mixes
        m = mixes
        table = np.zeros((n, m))
        
        self.raw_materials_count = raw_materials
        self.mixes_count = mixes
        self.total_rows = n
        self.total_cols = m
        
        return table


def main():
    """
    Main function to demonstrate the algorithm with the example from the article.
    """
    product_name = "Product1"
    mrc = MaterialRequirementsCalculations(product_name)
    
    # Target amount 
    target_amount = 1000.0
    target_table = mrc.calculate_material_requirements(target_amount)
    
    
    # Print results
    mrc.print_results(mrc.percentage_table, target_table, target_amount)
   

if __name__ == "__main__":
    main() 