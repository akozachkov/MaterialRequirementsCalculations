import os
import numpy as np
import csv

'''
process_product_data.py
Updated 2025-08-06 15:10
'''

class ProductTableReaderWriter:
    """
    Class to read a product CSV file and convert it into a structured format.
    The CSV should have:
        - First row: ['', 'Mix 1', 'Mix 2', ...]
        - First column: Ingredient names
        - Remaining cells: numeric values for ingredient quantities
    """

    def __init__(self, product_filename: str, products_dir: str = "products"):
        """
        Initialize the reader with the product file name and optional products directory.
        :param product_filename: Name of the product file (e.g., 'Product1.csv')
        :param products_dir: Directory where product files are stored (default 'products')
        """
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.file_path = os.path.join(script_dir, products_dir, product_filename + ".csv")
        self.percentage_table = None
        self.ingredient_names = []
        self.mix_names = []

    def read(self):
        """
        Reads the product CSV file and populates the table, ingredient names, and mix names.
        """
        with open(self.file_path, newline='') as csvfile:
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

            # Convert data to NumPy array
            self.percentage_table = np.array(data_rows, dtype=float)

        if (self._validate_percentage_table()):
            return self.percentage_table, self.ingredient_names, self.mix_names
        else:
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

    def writeTargetTable(self, target_table):
        """
        TODO
        Writes the product calculated CSV file including ingridients, mixees, Bill of Material

        """

# Example usage:
if __name__ == "__main__":
    reader = ProductTableReaderWriter("Product1", "products")
    percentage_table, ingredient_names, mix_names = reader.read()
    print(percentage_table)
    print(ingredient_names)
    print(mix_names)