import csv
from datetime import datetime
import os

import numpy as np

'''
process_product_data.py
Updated 2025-08-07 16:24
'''

DEFAULT_PRODUCTS_DIRECTORY = "products"
DEFAULT_CALCULATIONS_DIRECTORY = "calculation_requests"

class ProductTableReaderWriter:
    """
    Class to read a product CSV file and convert it into a structured format.
    The CSV should have:
        - First row: ['', 'Mix 1', 'Mix 2', ...]
        - First column: Ingredient names
        - Remaining cells: numeric values for ingredient quantities
    """

    def __init__(self, product_filename: str, products_dir: str = DEFAULT_PRODUCTS_DIRECTORY, \
        calculation_requests_dir: str = DEFAULT_CALCULATIONS_DIRECTORY):
        """
        Initialize the reader with the product file name and optional products directory.
        :param product_filename: Name of the product file (e.g., 'Product1.csv')
        :param products_dir: Directory where product files are stored (default 'products')
        """
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.product_file_path = os.path.join(script_dir, products_dir, product_filename + ".csv")
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename_with_timestamp = f"{product_filename}_{timestamp}.txt"
        self.calculation_request_file_path = os.path.join(script_dir, calculation_requests_dir, filename_with_timestamp)

        self.percentage_table = None
        self.raw_material_names = []
        self.mix_names = []
        self.ingredient_names = [] # it's really the sum of raw_materials and mixes        

    def read(self):
        """
        Reads the product CSV file and populates the table, ingredient names, and mix names.
        """
        with open(self.product_file_path, newline='') as csvfile:
            reader = list(csv.reader(csvfile))

            # Extract mix names (skip the first empty column)
            self.mix_names = [name for name in reader[0][1:] if name.strip()]
            mixes_count = len(self.mix_names)

            # Extract ingredient names and data rows
            data_rows = []
            for row in reader[1:]:
                if row[0].strip():  # Non-empty ingredient name
                    self.ingredient_names.append(row[0].strip())
                    data_rows.append([
                        float(cell) if cell.strip() else 0.0
                        for cell in row[1:1 + mixes_count]
                    ])

            # raw_material_names are all the igridents less mixes
            self.raw_material_names = [name for name in self.ingredient_names if name not in self.mix_names]

            # Convert data to NumPy array
            self.percentage_table = np.array(data_rows, dtype=float)

        if (not self._validate_percentage_table()):  
            raise ValueError("Invalid percentage table")        

    def _validate_percentage_table(self) -> bool:
        """
        Validate that the percentage table meets the requirements.
        
        Args:
            table: The percentage table P
            
        Returns:
            bool: True if valid, False otherwise
        """
        if self.percentage_table.ndim != 2:
            print("Error: Table must be 2-dimensional")
            return False
        
        n, m = self.percentage_table.shape
        self.raw_materials_count = n - m
        self.mixes_count = m
        self.total_rows = n
        self.total_cols = m
        
        # Check that each column sums to 100 for the defined elements
        for j in range(m):
            # For column j, we need to check only the non-zero elements
            # The table structure shows that not all ingredients are used in each mix
            column = self.percentage_table[:, j]
            # Only consider non-zero elements as defined for this mix
            non_zero_elements = column[column != 0]
            #print(f"Column {j+1}: {column}")
            #print(f"  Non-zero elements: {non_zero_elements} (sum = {np.sum(non_zero_elements)})")
            if not np.isclose(np.sum(non_zero_elements), 100.0, atol=1e-6):
                print(f"Error: Column {j+1} does not sum to 100. Sum = {np.sum(non_zero_elements)}")
                return False
            #print(f"  ✓ Column {j+1} is valid")
        
        print(f"Valid table: {self.raw_materials_count} raw materials, {self.mixes_count} mixes")
        return True

    def writeCalculationRequest(self, results_string):
        """
        Writes the product calculated CSV file including ingridients, mixees, Bill of Material
        """
        with open(self.calculation_request_file_path, "w", encoding="utf-8") as f:
            f.write(results_string)

# Example usage:
if __name__ == "__main__":
    reader = ProductTableReaderWriter("Product1", "products")
    reader.read()
    print("\npercentage_table:\n" + str(reader.percentage_table))    
    print("\nraw_material_names:\n" + str(reader.raw_material_names))
    print("\nmix_names:\n" + str(reader.mix_names))
    print("\ningredient_names:\n" + str(reader.ingredient_names))