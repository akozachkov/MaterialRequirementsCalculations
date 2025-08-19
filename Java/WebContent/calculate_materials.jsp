<%@ page import="com.kozachkov.material_requirements.MaterialRequirementsCalculations" %>
<%@ page contentType="text/html;charset=UTF-8" language="java" %>
<html>
<head>
    <title>Material Calculator</title>
</head>
<body>
    <h2>Calculate Material Requirements</h2>

    <form method="post" action="calculate_materials.jsp">
        <label for="productName">Choose Product:</label>
        <select name="productName" id="productName">
            <option value="ArticleExampleProduct" <%= "ArticleExampleProduct".equals(request.getParameter("productName")) ? "selected" : "" %>>ArticleExampleProduct</option>
            <option value="OrigWebExample" <%= "OrigWebExample".equals(request.getParameter("productName")) ? "selected" : "" %>>OrigWebExample</option>
        </select>
        <br/><br/>

        <label for="targetAmount">Target Product Amount:</label>
        <input type="text" name="targetAmount" id="targetAmount"
               value="<%= request.getParameter("targetAmount") != null ? request.getParameter("targetAmount") : "" %>" />
        <br/><br/>

        <input type="submit" value="Calculate" />
    </form>

    <hr/>

    <%
        String productName = request.getParameter("productName");
        String targetAmountStr = request.getParameter("targetAmount");

        if (productName != null && targetAmountStr != null && !targetAmountStr.isEmpty()) {
            try {
                float targetAmount = Float.parseFloat(targetAmountStr);

                // The app’s root directory (your "materials_app" folder under webapps)
                String appPath = application.getRealPath("/");

                MaterialRequirementsCalculations calc =
                    new MaterialRequirementsCalculations(appPath, productName);

                String result = calc.calculateBOM(targetAmount);

                out.println("<h3>Results for " + productName + " (" + targetAmount + " units)</h3>");
                out.println("<pre>" + result + "</pre>");
            } catch (Exception e) {
                out.println("<p style='color:red'>Error: " + e.getMessage() + "</p>");
            }
        }
    %>
</body>
</html>
