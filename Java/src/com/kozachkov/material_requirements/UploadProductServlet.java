package com.kozachkov.material_requirements;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import javax.servlet.ServletException;
import javax.servlet.annotation.MultipartConfig;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.servlet.http.Part;

/**
 * Updated 2025-08-21 12:18
 */

@WebServlet("/uploadProduct")
@MultipartConfig
public class UploadProductServlet extends HttpServlet {

    private static final int BUFFER_SIZE = 1024;

    @Override
    protected void doPost(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {

        Part filePart = request.getPart("file");
        String fileName = getFileName(filePart); // Safe filename extraction

        // Path to your "products" directory inside the web app
        String productsDir = getServletContext().getRealPath("/products");
        File uploadDir = new File(productsDir);
        if (!uploadDir.exists()) {
            uploadDir.mkdirs();
        }

        File file = new File(uploadDir, fileName);

        try (InputStream input = filePart.getInputStream();
                FileOutputStream output = new FileOutputStream(file)) {
            byte[] buffer = new byte[BUFFER_SIZE];
            int bytesRead;
            while ((bytesRead = input.read(buffer)) != -1) {
                output.write(buffer, 0, bytesRead);
            }
        }

        response.setContentType("text/html");
        response.getWriter().println("<html><body>");
        response.getWriter()
                .println("<link rel=\"stylesheet\" type=\"text/css\" href=\"styles/MaterialAppStyles.css\">");

        response.getWriter().println("<h3>Upload successful: " + fileName + "</h3>");
        // response.getWriter().println("<a href='index.html'>Back to Home</a>");
        response.getWriter().println("<a class=\"menu-link\" href=\"index.html\">&#x1F3E0; Back to Home</a>");

        response.getWriter().println("</body></html>");
    }

    // Helper for compatibility with older servlet APIs
    private String getFileName(Part part) {
        String contentDisp = part.getHeader("content-disposition");
        if (contentDisp != null) {
            for (String cd : contentDisp.split(";")) {
                if (cd.trim().startsWith("filename")) {
                    return cd.substring(cd.indexOf('=') + 1).trim().replace("\"", "");
                }
            }
        }
        return "unknown";
    }
}
