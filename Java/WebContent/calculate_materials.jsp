<%@ page import="java.io.File" %>
<%@ page import="com.kozachkov.material_requirements.MaterialRequirementsCalculations" %>
<%@ page contentType="text/html;charset=UTF-8" language="java" %>
<!DOCTYPE html>
<html lang="en">
<!-- 8/19/2025 20:30 -->
<head>
    <meta charset="UTF-8">
    <title>Material Calculator</title>

<link rel="stylesheet" type="text/css" href="styles/MaterialAppStyles.css">

    
</head>
<body>
    <h1>Calculate Material Requirements</h1>

    <%
        // Get the application root (e.g., webapps/materials_app/)
        String appPath = application.getRealPath("/");

        // The products directory (adjust if needed)
        File productsDir = new File(appPath, "products");

        // Ensure directory exists
        String[] productFiles = productsDir.exists() ? productsDir.list() : new String[0];

        // Remember previous user selection
        String selectedProduct = request.getParameter("productName");
        String targetAmountParam = request.getParameter("targetAmount");
    %>

    <form method="post" action="calculate_materials.jsp">
        <label for="productName">Choose Product:</label>
        <select name="productName" id="productName" required>
            <%
                if (productFiles != null) {
                    for (String file : productFiles) {
                        if (file.toLowerCase().endsWith(".csv")) {
                            // Strip extension to show cleaner names
                            String productName = file.replaceFirst("\\.csv$", "");
                            String selected = productName.equals(selectedProduct) ? "selected" : "";
            %>
                            <option value="<%= productName %>" <%= selected %>><%= productName %></option>
            <%
                        }
                    }
                }
            %>
        </select>

        <label for="targetAmount">Target Product Amount:</label>
        <input type="text" name="targetAmount" id="targetAmount"
               value="<%= targetAmountParam != null ? targetAmountParam : "" %>" required />

        <input type="submit" value="Calculate" />
    </form>

    <%
        if (selectedProduct != null && targetAmountParam != null && !targetAmountParam.isEmpty()) {
            try {
                float targetAmount = Float.parseFloat(targetAmountParam);

                MaterialRequirementsCalculations calc =
                    new MaterialRequirementsCalculations(appPath, selectedProduct);

                String result = calc.calculateBOM(targetAmount);
    %>
                <div class="results">
                    <h2>Results for <%= selectedProduct %> (<%= targetAmount %> units)</h2>
                    <pre><%= result %></pre>
                </div>
    <%
            } catch (Exception e) {
    %>
                <p class="error">Error: <%= e.getMessage() %></p>
    <%
            }
        }
    %>

    <a class="menu-link" href="index.html">🏠 Back to Home</a>
</body>
</html>
