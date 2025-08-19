package com.kozachkov.material_requirements;

import java.io.*;
import java.nio.file.*;
import java.text.SimpleDateFormat;
import java.util.*;

/**
 * ProductTableReaderWriter.java
 * Updated 2025-08-19 8:15
 *
 * Class to read a product CSV file and convert it into a structured format.
 * The CSV should have:
 * - First row: ['', 'Mix 1', 'Mix 2', ...]
 * - First column: Ingredient names
 * - Remaining cells: numeric values for ingredient quantities
 */
public class ProductTableReaderWriter {

    private static final String PRODUCTS_DIRECTORY = "products";
    private static final String CALCULATIONS_DIRECTORY = "calculation_requests";

    private final String materialsAppDirectoryPath;
    private final String productFilePath;
    private final String calculationRequestFilePath;

    private double[][] percentageTable;
    private List<String> rawMaterialNames;
    private List<String> mixNames;
    private List<String> ingredientNames;

    private int rawMaterialsCount;
    private int mixesCount;
    private int totalRows;
    private int totalCols;

    public ProductTableReaderWriter(String materialsAppDirectoryPath, String productFilename) throws IOException {
        this.materialsAppDirectoryPath = materialsAppDirectoryPath;

        Path baseDir = Paths.get(materialsAppDirectoryPath).toAbsolutePath();
        this.productFilePath = baseDir.resolve(Paths.get(PRODUCTS_DIRECTORY, productFilename + ".csv")).toString();

        String timestamp = new SimpleDateFormat("yyyyMMddHHmmss").format(new Date());
        String filenameWithTimestamp = productFilename + "_" + timestamp + ".txt";
        this.calculationRequestFilePath = baseDir.resolve(Paths.get(CALCULATIONS_DIRECTORY, filenameWithTimestamp))
                .toString();

        this.rawMaterialNames = new ArrayList<>();
        this.mixNames = new ArrayList<>();
        this.ingredientNames = new ArrayList<>();
    }

    /**
     * Reads the product CSV file and populates the table, ingredient names, and mix
     * names.
     */
    public void read() throws IOException {
        List<String[]> rows = new ArrayList<>();

        try (BufferedReader br = new BufferedReader(new FileReader(this.productFilePath))) {
            String line;
            while ((line = br.readLine()) != null) {
                rows.add(line.split(","));
            }
        }

        if (rows.isEmpty()) {
            throw new IOException("CSV file is empty: " + this.productFilePath);
        }

        // Extract mix names (skip the first empty column)
        String[] header = rows.get(0);
        for (int i = 1; i < header.length; i++) {
            if (!header[i].trim().isEmpty()) {
                this.mixNames.add(header[i].trim());
            }
        }
        mixesCount = this.mixNames.size();

        // Extract ingredient names and data rows
        List<double[]> dataRows = new ArrayList<>();
        for (int i = 1; i < rows.size(); i++) {
            String[] row = rows.get(i);
            if (row.length == 0)
                continue;
            String ingredientName = row[0].trim();
            if (!ingredientName.isEmpty()) {
                this.ingredientNames.add(ingredientName);
                double[] values = new double[mixesCount];
                for (int j = 0; j < mixesCount; j++) {
                    if (j + 1 < row.length && !row[j + 1].trim().isEmpty()) {
                        try {
                            values[j] = Double.parseDouble(row[j + 1].trim());
                        } catch (NumberFormatException e) {
                            values[j] = 0.0;
                        }
                    } else {
                        values[j] = 0.0;
                    }
                }
                dataRows.add(values);
            }
        }

        // raw_material_names = ingredients - mixes
        for (String ing : this.ingredientNames) {
            if (!this.mixNames.contains(ing)) {
                this.rawMaterialNames.add(ing);
            }
        }

        // Convert to 2D array
        this.percentageTable = new double[dataRows.size()][mixesCount];
        for (int i = 0; i < dataRows.size(); i++) {
            this.percentageTable[i] = dataRows.get(i);
        }

        if (!this.validatePercentageTable()) {
            throw new IllegalArgumentException("Invalid percentage table");
        }
    }

    /**
     * Validate that the percentage table meets the requirements.
     */
    private boolean validatePercentageTable() {
        if (percentageTable == null) {
            System.err.println("Error: Table is null");
            return false;
        }

        int n = percentageTable.length;
        if (n == 0) {
            System.err.println("Error: Table has no rows");
            return false;
        }

        int m = percentageTable[0].length;
        this.rawMaterialsCount = n - m;
        this.mixesCount = m;
        this.totalRows = n;
        this.totalCols = m;

        for (int j = 0; j < m; j++) {
            double sum = 0.0;
            for (int i = 0; i < n; i++) {
                double val = percentageTable[i][j];
                if (val != 0.0) {
                    sum += val;
                }
            }
            if (Math.abs(sum - 100.0) > 1e-6) {
                System.err.printf("Error: Column %d does not sum to 100. Sum = %.6f%n", j + 1, sum);
                return false;
            }
        }

        System.out.printf("Valid table: %d raw materials, %d mixes%n", rawMaterialsCount, mixesCount);
        return true;
    }

    /**
     * Writes the product calculation request file including ingredients, mixes, BOM
     */
    public void writeCalculationRequest(String resultsString) throws IOException {
        try (BufferedWriter writer = new BufferedWriter(new FileWriter(this.calculationRequestFilePath))) {
            writer.write(resultsString);
        }
    }

    // Getters for inspection
    public double[][] getPercentageTable() {
        return percentageTable;
    }

    public List<String> getRawMaterialNames() {
        return rawMaterialNames;
    }

    public List<String> getMixNames() {
        return mixNames;
    }

    public List<String> getIngredientNames() {
        return ingredientNames;
    }

    // Example usage
    public static void main(String[] args) {
        try {
            // Example: local path
            String localBase = "C:\\Temp\\GitHubRepositories\\MaterialRequirementsCalculations\\Java";
            ProductTableReaderWriter reader = new ProductTableReaderWriter(localBase, "ArticleExampleProduct");

            reader.read();
            System.out.println("\npercentage_table:");
            System.out.println(Arrays.deepToString(reader.getPercentageTable()));

            System.out.println("\nraw_material_names:");
            System.out.println(reader.getRawMaterialNames());

            System.out.println("\nmix_names:");
            System.out.println(reader.getMixNames());

            System.out.println("\ningredient_names:");
            System.out.println(reader.getIngredientNames());

        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}