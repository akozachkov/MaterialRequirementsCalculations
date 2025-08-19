package com.kozachkov.material_requirements;

import java.io.IOException;
import java.util.*;

/**
 * MaterialRequirementsCalculations.java
 * Updated 2025-08-19, 8:15
 *
 * Implementation of the linear algorithm to calculate material requirements
 * for processes defined on a table of mixes and ingredients.
 *
 * Based on the algorithm described in:
 * "A Linear Algorithm to Calculate Material Requirements for Processes Defined
 * on a Table of Mixes and Ingredients"
 * by Alexander L. Kozachkov and Leo A. Kozachkov
 * http://kozachkov.com/Alex/linear-algorithm-calculate.pdf
 */
public class MaterialRequirementsCalculations {
    private static final double DEFAULT_TARGET_AMOUNT = 100.0;

    protected String materials_app_directory_path; // e.g. "./webapps/materials_app"
    private String productName;
    private ProductTableReaderWriter reader;

    private double[][] percentageTable;
    private List<String> rawMaterialNames;
    private List<String> mixNames;
    private List<String> ingredientNames;

    private int rawMaterialCount;
    private int mixesCount;
    private int ingredientCount;

    /**
     * New constructor that accepts application directory path and product name.
     */
    public MaterialRequirementsCalculations(String materials_app_directory_path, String productName)
            throws IOException {
        this.materials_app_directory_path = materials_app_directory_path;
        this.productName = productName;
        this.reader = new ProductTableReaderWriter(materials_app_directory_path, productName);
        this.reader.read();

        this.percentageTable = reader.getPercentageTable();
        this.rawMaterialNames = reader.getRawMaterialNames();
        this.mixNames = reader.getMixNames();
        this.ingredientNames = reader.getIngredientNames();

        this.rawMaterialCount = rawMaterialNames.size();
        this.mixesCount = mixNames.size();
        this.ingredientCount = ingredientNames.size();
    }

    /**
     * Calculate material requirements using the linear algorithm.
     */
    private double[][] calculateMaterialRequirements(double targetAmount) {
        int n = percentageTable.length;
        int m = percentageTable[0].length;

        double[][] targetTable = new double[n][m];

        // Step 1: Calculate the last mix (target product)
        double mix_m_total = 0.0;
        for (int i = 0; i < n; i++) {
            targetTable[i][m - 1] = targetAmount * percentageTable[i][m - 1] / 100.0;
            mix_m_total += targetTable[i][m - 1];
        }

        if (Math.abs(mix_m_total - targetAmount) > 1e-6) {
            throw new IllegalArgumentException("Last mix did not match target_amount: " + mix_m_total +
                    " vs. " + targetAmount);
        }

        System.out.printf("%nStep 1: Last mix (Mix %d) calculated%n", m);
        System.out.println("Target amount: " + targetAmount);
        System.out.println("Mix " + m + " amounts: " + Arrays.toString(getColumn(targetTable, m - 1)));

        // Step 2: Calculate remaining mixes working backwards
        int currentTableRowWithMix = n - 1;
        for (int j = m - 2; j >= 0; j--) {
            currentTableRowWithMix -= 1;
            double mix_j_amount = 0.0;
            for (int col = 0; col < m; col++) {
                mix_j_amount += targetTable[currentTableRowWithMix][col];
            }

            System.out.printf("%nStep %d: Calculating Mix %d%n", (m - j), (j + 1));
            System.out.println("Mix " + (j + 1) + " amount needed: " + mix_j_amount);

            for (int i = 0; i < Math.min(n + j + 1, targetTable.length); i++) {
                targetTable[i][j] = mix_j_amount * percentageTable[i][j] / 100.0;
            }

            targetTable[currentTableRowWithMix][j] = mix_j_amount;
        }

        return targetTable;
    }

    /**
     * Calculate the total amount of each raw material needed.
     */
    private double[] getRawMaterialTotals(double[][] targetTable) {
        double[] totals = new double[rawMaterialCount];
        for (int i = 0; i < rawMaterialCount; i++) {
            double sum = 0.0;
            for (int j = 0; j < targetTable[0].length; j++) {
                sum += targetTable[i][j];
            }
            totals[i] = sum;
        }
        return totals;
    }

    /**
     * Generate the results as a formatted string.
     */
    private String getResultsString(double[][] percentageTable, double[][] targetTable, double targetAmount) {
        StringBuilder sb = new StringBuilder();
        sb.append("\n").append("=".repeat(80)).append("\n");
        sb.append("MATERIAL REQUIREMENTS PLANNING RESULTS\n");
        sb.append("Target Amount: ").append(targetAmount).append("\n");
        sb.append("=".repeat(80)).append("\n");

        // Percentage Table
        sb.append("\nPERCENTAGE TABLE (Original):\n");
        sb.append("-".repeat(65)).append("\n");

        sb.append(String.format("%-15s", ""));
        for (String header : mixNames) {
            sb.append(String.format("%10s", header));
        }
        sb.append("\n");

        for (int i = 0; i < ingredientNames.size(); i++) {
            sb.append(String.format("%-15s", ingredientNames.get(i)));
            for (int j = 0; j < mixesCount; j++) {
                sb.append(String.format("%10.1f", percentageTable[i][j]));
            }
            sb.append("\n");
        }

        // Target Table
        sb.append("\nTARGET TABLE (Calculated):\n");
        sb.append("-".repeat(65)).append("\n");

        List<String> headersWithBOM = new ArrayList<>(mixNames);
        headersWithBOM.add("BOM");

        sb.append(String.format("%-15s", ""));
        for (String header : headersWithBOM) {
            sb.append(String.format("%10s", header));
        }
        sb.append("\n");

        double[] rawMaterialTotals = getRawMaterialTotals(targetTable);
        for (int i = 0; i < ingredientNames.size(); i++) {
            sb.append(String.format("%-15s", ingredientNames.get(i)));
            for (int j = 0; j < mixesCount; j++) {
                sb.append(String.format("%10.1f", targetTable[i][j]));
            }
            if (i < rawMaterialTotals.length) {
                sb.append(String.format("%10.1f", rawMaterialTotals[i]));
            } else {
                sb.append(String.format("%10s", "n/a"));
            }
            sb.append("\n");
        }

        sb.append("\nTotal raw materials needed: ")
                .append(String.format("%.1f", Arrays.stream(rawMaterialTotals).sum()))
                .append("\n");

        sb.append("\n").append("=".repeat(80)).append("\n\n");

        return sb.toString();
    }

    /**
     * Encapsulate the entire process.
     */
    public String calculateBOM(double targetAmount) throws IOException {
        double[][] targetTable = calculateMaterialRequirements(targetAmount);

        String resultsString = getResultsString(percentageTable, targetTable, targetAmount);
        //System.out.println(resultsString);

        reader.writeCalculationRequest(resultsString);
        return resultsString;
    }

    private static double[] getColumn(double[][] matrix, int col) {
        double[] column = new double[matrix.length];
        for (int i = 0; i < matrix.length; i++) {
            column[i] = matrix[i][col];
        }
        return column;
    }

    public static void main(String[] args) {
        String productName = "ArticleExampleProduct";
        double targetAmount = 3000;

        // Example local path
        String localAppDir = 
        "C:\\Temp\\GitHubRepositories\\MaterialRequirementsCalculations\\Java\\WebContent";

        try {
            MaterialRequirementsCalculations mrc = new MaterialRequirementsCalculations(localAppDir, productName);
            String resultsString = mrc.calculateBOM(targetAmount);
            System.out.println(resultsString);

        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
