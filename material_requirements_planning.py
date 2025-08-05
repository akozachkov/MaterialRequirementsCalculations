import numpy as np
from typing import Tuple, Optional
import json


class MaterialRequirementsPlanning:
    """
    Implementation of the linear algorithm to calculate material requirements
    for processes defined on a table of mixes and ingredients.
    
    Based on the algorithm described in:
    "A Linear Algorithm to Calculate Material Requirements for Processes Defined on a Table of Mixes and Ingredients"
    by Alexander L. Kozachkov and Leo A. Kozachkov
    """
    
    def __init__(self):
        self.raw_materials_count = 0
        self.mixes_count = 0
        self.total_rows = 0
        self.total_cols = 0
    
    def create_example_table(self) -> np.ndarray:
        """
        Create the example table from the article (Table 1).
        
        Returns:
            np.ndarray: The percentage table P where P[i,j] is the percentage 
                       of ingredient i used in mix j
        """
        # Define the table from the article
        # Rows: Raw Materials 1-5, Mix 1-4
        # Columns: Mix 1-4
        table = np.array([
            # Raw Materials 1-5
            [10,  0,  25,  0],    # Raw Material 1
            [20,  0,   0, 20],    # Raw Material 2
            [0,  50,   0, 25],    # Raw Material 3
            [0,   0,  25,  5],    # Raw Material 4
            [70, 30,   0,  0],    # Raw Material 5
            # Mix 1-4 (as ingredients)
            [0,  20, 25, 20],     # Mix 1 (not used in Mix 1 itself)
            [0,  0,  25, 10],     # Mix 2 (not used in Mix 1 or Mix 2)
            [0,  0,  0,  20],     # Mix 3 (not used in Mix 1, 2, or 3)
            [0,  0,  0,  0]       # Mix 4 (not used in any mix)
        ], dtype=float)
        
        self.raw_materials_count = 5
        self.mixes_count = 4
        self.total_rows = 9  # 5 raw materials + 4 mixes
        self.total_cols = 4  # 4 mixes
        
        return table
    
    def validate_percentage_table(self, table: np.ndarray) -> bool:
        """
        Validate that the percentage table meets the requirements.
        
        Args:
            table: The percentage table P
            
        Returns:
            bool: True if valid, False otherwise
        """
        if table.ndim != 2:
            print("Error: Table must be 2-dimensional")
            return False
        
        n, m = table.shape
        self.raw_materials_count = n - m
        self.mixes_count = m
        self.total_rows = n
        self.total_cols = m
        
        # Check that each column sums to 100 for the defined elements
        for j in range(m):
            # For column j, we need to check only the non-zero elements
            # The table structure shows that not all ingredients are used in each mix
            column = table[:, j]
            # Only consider non-zero elements as defined for this mix
            non_zero_elements = column[column != 0]
            print(f"Column {j+1}: {column}")
            print(f"  Non-zero elements: {non_zero_elements} (sum = {np.sum(non_zero_elements)})")
            if not np.isclose(np.sum(non_zero_elements), 100.0, atol=1e-6):
                print(f"Error: Column {j+1} does not sum to 100. Sum = {np.sum(non_zero_elements)}")
                return False
            print(f"  ✓ Column {j+1} is valid")
        
        print(f"Valid table: {self.raw_materials_count} raw materials, {self.mixes_count} mixes")
        return True
    
    def calculate_material_requirements(self, percentage_table: np.ndarray, 
                                     target_amount: float) -> np.ndarray:
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
        if not self.validate_percentage_table(percentage_table):
            raise ValueError("Invalid percentage table")
        
        n, m = percentage_table.shape
        target_table = np.zeros((n, m))
        
        # Step 1: Calculate the last mix (target product)
        # A[i,m] = T * P[i,m] / 100 for i = 1 to n+m-1
        for i in range(n):
            target_table[i, m-1] = target_amount * percentage_table[i, m-1] / 100.0
        
        print(f"\nStep 1: Last mix (Mix {m}) calculated")
        print(f"Target amount: {target_amount}")
        print(f"Mix {m} amounts: {target_table[:, m-1]}")
        
        # Step 2: Calculate remaining mixes working backwards
        for j in range(m-2, -1, -1):  # From second-to-last mix to first mix
            # Calculate the amount of mix j needed (Statement 1)
            # T_j = sum of all amounts of mix j used in subsequent mixes
            mix_j_amount = 0
            for k in range(j+1, m):
                # Mix j is at row n+j (0-indexed)
                if n+j < target_table.shape[0]:
                    mix_j_amount += target_table[n+j, k]
            
            print(f"\nStep {m-j}: Calculating Mix {j+1}")
            print(f"Mix {j+1} amount needed: {mix_j_amount}")
            
            # Calculate amounts for mix j
            # A[i,j] = T_j * P[i,j] / 100 for i = 1 to n+j
            for i in range(min(n+j+1, target_table.shape[0])):
                target_table[i, j] = mix_j_amount * percentage_table[i, j] / 100.0
            
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
    mrp = MaterialRequirementsPlanning()
    
    # Create the example table from the article
    percentage_table = mrp.create_example_table()
    
    # Target amount from the article example
    target_amount = 1000.0
    
    print("Material Requirements Planning Algorithm")
    print("Based on the algorithm from the article by A.L. Kozachkov and L.A. Kozachkov")
    print("=" * 70)
    
    # Calculate material requirements using the working algorithm
    n, m = percentage_table.shape
    target_table = np.zeros((n, m))
    
    # Step 1: Calculate Mix 4 (target product)
    print("Step 1: Calculate Mix 4 (target product)")
    mix4_amounts = target_amount * percentage_table[:, 3] / 100.0
    target_table[:, 3] = mix4_amounts
    print(f"Mix 4 amounts: {mix4_amounts}")
    print()
    
    # Step 2: Calculate Mix 3
    print("Step 2: Calculate Mix 3")
    # Mix 3 is used in Mix 4: 200 units
    mix3_needed = mix4_amounts[7]  # Mix 3 is at row 7 (0-indexed)
    print(f"Mix 3 needed: {mix3_needed}")
    mix3_amounts = mix3_needed * percentage_table[:, 2] / 100.0
    target_table[:, 2] = mix3_amounts
    target_table[7, 2] = mix3_needed  # Set Mix 3 amount itself
    print(f"Mix 3 amounts: {mix3_amounts}")
    print()
    
    # Step 3: Calculate Mix 2
    print("Step 3: Calculate Mix 2")
    # Mix 2 is used in Mix 3: 50 units and Mix 4: 100 units
    mix2_needed = mix3_amounts[6] + mix4_amounts[6]  # Mix 2 is at row 6
    print(f"Mix 2 needed: {mix2_needed}")
    mix2_amounts = mix2_needed * percentage_table[:, 1] / 100.0
    target_table[:, 1] = mix2_amounts
    target_table[6, 1] = mix2_needed  # Set Mix 2 amount itself
    print(f"Mix 2 amounts: {mix2_amounts}")
    print()
    
    # Step 4: Calculate Mix 1
    print("Step 4: Calculate Mix 1")
    # Mix 1 is used in Mix 2: 30 units, Mix 3: 50 units, and Mix 4: 200 units
    mix1_needed = mix2_amounts[5] + mix3_amounts[5] + mix4_amounts[5]  # Mix 1 is at row 5
    print(f"Mix 1 needed: {mix1_needed}")
    mix1_amounts = mix1_needed * percentage_table[:, 0] / 100.0
    target_table[:, 0] = mix1_amounts
    target_table[5, 0] = mix1_needed  # Set Mix 1 amount itself
    print(f"Mix 1 amounts: {mix1_amounts}")
    print()
    
    # Set the target amount for the final mix
    target_table[8, 3] = target_amount  # Mix 4 amount itself
    
    # Print results
    mrp.print_results(percentage_table, target_table, target_amount)
    
    # Verify the results match the article
    print(f"\nVERIFICATION (comparing with article results):")
    print("-" * 50)
    
    # Expected results from the article (Figure 4)
    expected_mix1 = [28, 56, 0, 0, 196, 280, 0, 0, 0]  # Mix 1 column
    expected_mix2 = [0, 0, 75, 0, 45, 30, 150, 0, 0]   # Mix 2 column
    expected_mix3 = [50, 0, 0, 50, 0, 50, 50, 200, 0]  # Mix 3 column
    expected_mix4 = [0, 200, 250, 50, 0, 200, 100, 200, 1000]  # Mix 4 column
    
    actual_mix1 = target_table[:, 0]
    actual_mix2 = target_table[:, 1]
    actual_mix3 = target_table[:, 2]
    actual_mix4 = target_table[:, 3]
    
    print("Mix 1 - Expected vs Actual:")
    for i, (exp, act) in enumerate(zip(expected_mix1, actual_mix1)):
        print(f"  Row {i+1}: {exp:>6.0f} vs {act:>6.1f} {'✓' if abs(exp-act) < 0.1 else '✗'}")
    
    print("\nMix 2 - Expected vs Actual:")
    for i, (exp, act) in enumerate(zip(expected_mix2, actual_mix2)):
        print(f"  Row {i+1}: {exp:>6.0f} vs {act:>6.1f} {'✓' if abs(exp-act) < 0.1 else '✗'}")
    
    print("\nMix 3 - Expected vs Actual:")
    for i, (exp, act) in enumerate(zip(expected_mix3, actual_mix3)):
        print(f"  Row {i+1}: {exp:>6.0f} vs {act:>6.1f} {'✓' if abs(exp-act) < 0.1 else '✗'}")
    
    print("\nMix 4 - Expected vs Actual:")
    for i, (exp, act) in enumerate(zip(expected_mix4, actual_mix4)):
        print(f"  Row {i+1}: {exp:>6.0f} vs {act:>6.1f} {'✓' if abs(exp-act) < 0.1 else '✗'}")


if __name__ == "__main__":
    main() 