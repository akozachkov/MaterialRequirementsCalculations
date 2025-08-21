package com.kozachkov.material_requirements;

import java.io.File;
import java.io.IOException;
import java.io.Writer;
import java.util.ArrayList;
import java.util.List;

import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.thymeleaf.TemplateEngine;
import org.thymeleaf.context.Context;
import org.thymeleaf.templateresolver.FileTemplateResolver;
import org.thymeleaf.templatemode.TemplateMode;

/**
 * Servlet to replace JSP for material calculations
 * Uses Thymeleaf template: calculate_materials.html
 * Updated: 2025-08-20
 */
@WebServlet("/calculate")
public class MaterialRequirementsCalculationsServlet extends HttpServlet {

    private TemplateEngine templateEngine;

    @Override
    public void init() throws ServletException {
        // Resolve templates from /WEB-INF/templates on disk
        String templatePath = getServletContext().getRealPath("/WEB-INF/templates/");

        FileTemplateResolver templateResolver = new FileTemplateResolver();
        templateResolver.setPrefix(templatePath + "/");
        templateResolver.setSuffix(".html");
        templateResolver.setTemplateMode(TemplateMode.HTML);
        templateResolver.setCharacterEncoding("UTF-8");
        templateResolver.setCacheable(false); // disable cache during development

        templateEngine = new TemplateEngine();
        templateEngine.setTemplateResolver(templateResolver);
    }

    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse resp)
            throws ServletException, IOException {
        processRequest(req, resp, false);
    }

    @Override
    protected void doPost(HttpServletRequest req, HttpServletResponse resp)
            throws ServletException, IOException {
        processRequest(req, resp, true);
    }

    private void processRequest(HttpServletRequest req, HttpServletResponse resp, boolean isPost)
            throws ServletException, IOException {

        String appPath = getServletContext().getRealPath("");
        Context ctx = new Context();

        // Load available CSV products from /products directory
        List<String> productFiles = loadProductFiles(appPath);
        ctx.setVariable("productFiles", productFiles);

        // Default values
        String selectedProduct = "";
        String targetAmount = "";
        String result = null;
        String error = null;

        if (isPost) {
            selectedProduct = req.getParameter("product");
            targetAmount = req.getParameter("targetAmount");

            if (selectedProduct != null && !selectedProduct.isEmpty()
                    && targetAmount != null && !targetAmount.isEmpty()) {
                try {
                    MaterialRequirementsCalculations calc =
                            new MaterialRequirementsCalculations(appPath, selectedProduct);

                    float targetAmountFloat = Float.parseFloat(targetAmount);
                    result = calc.calculateBOM(targetAmountFloat);
                } catch (Exception e) {
                    error = "Error: " + e.getMessage();
                }
            }
        }

        // Pass variables to Thymeleaf template
        ctx.setVariable("selectedProduct", selectedProduct);
        ctx.setVariable("targetAmount", targetAmount);
        ctx.setVariable("result", result);
        ctx.setVariable("error", error);

        // Render template
        resp.setContentType("text/html;charset=UTF-8");
        resp.setCharacterEncoding("UTF-8");
        Writer out = resp.getWriter();
        templateEngine.process("calculate_materials", ctx, out);
    }

    private List<String> loadProductFiles(String appPath) {
        List<String> productFiles = new ArrayList<>();
        File productsDir = new File(appPath, "products");
        if (productsDir.exists() && productsDir.isDirectory()) {
            String[] files = productsDir.list();
            if (files != null) {
                for (String file : files) {
                    if (file.toLowerCase().endsWith(".csv")) {
                        productFiles.add(file.replaceFirst("\\.csv$", ""));
                    }
                }
            }
        }
        return productFiles;
    }
}
