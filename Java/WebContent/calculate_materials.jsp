<%@ page import="java.io.File" %>
<%@ page import="com.kozachkov.material_requirements.MaterialRequirementsCalculations" %>
<%@ page contentType="text/html;charset=UTF-8" language="java" %>
<html>
<!-- 8/19/2025 14:07-->
<head>
    <title>Material Calculator</title>
</head>
<body>
    <h2>Calculate Material Requirements</h2>

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
        <select name="productName" id="productName">
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
        <br/><br/>

        <label for="targetAmount">Target Product Amount:</label>
        <input type="text" name="targetAmount" id="targetAmount"
               value="<%= targetAmountParam != null ? targetAmountParam : "" %>" />
        <br/><br/>

        <input type="submit" value="Calculate" />
    </form>

    <hr/>

    <%
        if (selectedProduct != null && targetAmountParam != null && !targetAmountParam.isEmpty()) {
            try {
                float targetAmount = Float.parseFloat(targetAmountParam);

                MaterialRequirementsCalculations calc =
                    new MaterialRequirementsCalculations(appPath, selectedProduct);

                String result = calc.calculateBOM(targetAmount);

                out.println("<h3>Results for " + selectedProduct + " (" + targetAmount + " units)</h3>");
                out.println("<pre>" + result + "</pre>");
            } catch (Exception e) {
                out.println("<p style='color:red'>Error: " + e.getMessage() + "</p>");
            }
        }
    %>
</body>
</html>
